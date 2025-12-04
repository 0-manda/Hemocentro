import re
import jwt
import os
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, g
from back.utils.validators import only_numbers, is_cnpj, is_cpf
from dotenv import load_dotenv

load_dotenv()
# jwt config
SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = 'HS256'
TOKEN_EXPIRATION_HOURS = 24

# validação cpf e cnpj
def mascara_cnpj(cnpj: str) -> str:
    if not cnpj:
        return "N/A"
    num = only_numbers(cnpj)
    if len(num) == 14:
        return f"**.***.***/0001-{num[10:]}"
    return "***"

def validar_cpf_cnpj_usuario(cpf: str, cnpj: str, tipo_usuario: str):
    if tipo_usuario == 'colaborador':
        # CNPJ obrigatório
        if not cnpj:
            return False, "CNPJ é obrigatório para colaboradores"
        if not is_cnpj(cnpj):
            return False, "CNPJ inválido"
        # CPF opcional - valida apenas se fornecido
        if cpf and not is_cpf(cpf):
            return False, "CPF inválido"
        return True, ""
    elif tipo_usuario == 'doador':
        # CPF obrigatório
        if not cpf:
            return False, "CPF é obrigatório para doadores"
        if not is_cpf(cpf):
            return False, "CPF inválido"
        # CNPJ não permitido
        if cnpj:
            return False, "Doadores não podem ter CNPJ"
        return True, ""
    return False, "Tipo de usuário inválido"

def validar_cnpj_hemocentro(cnpj: str) -> tuple[bool, str]:
    cnpj = (cnpj or '').strip()
    if not cnpj:
        return False, "CNPJ é obrigatório"
    if not is_cnpj(cnpj):
        return False, "CNPJ inválido"
    return True, ""

# hash de senha (bycript)
def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verificar_senha(senha: str, senha_hash: str) -> bool:
    return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))

# jwt
def gerar_token(id_usuario: int, tipo_usuario: str, nome: str, email: str) -> str:
    payload = {
        'id_usuario': id_usuario,
        'tipo_usuario': tipo_usuario,
        'nome': nome,
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRATION_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    
#############################################################################################

# decorators
def token_required(f):
    from back.models import UsuarioModel, HemocentroModel
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer TOKEN"
            except IndexError:
                return jsonify({
                    "success": False,
                    "message": "Formato de token inválido"
                }), 401
        if not token:
            return jsonify({
                "success": False,
                "message": "Token não fornecido, faça login."
            }), 401
        try:
            current_user = verificar_token(token)
            if not current_user:
                return jsonify({
                    "success": False,
                    "message": "Token inválido ou expirado."
                }), 401
            usuario = UsuarioModel.buscar_por_id(current_user['id_usuario'])
            if not usuario or not usuario.get('ativo', True):
                return jsonify({
                    "success": False,
                    "message": "Usuário inválido ou inativo"
                }), 403
            g.current_user = usuario
            g.id_usuario = usuario['id_usuario']
            g.tipo_usuario = usuario['tipo_usuario']
            g.nome = usuario['nome']
            g.email = usuario['email']
            if usuario['tipo_usuario'] == 'colaborador':
                cnpj = usuario.get('cnpj')
                if cnpj:
                    hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
                    if hemocentro:
                        g.hemocentro = hemocentro
                        g.id_hemocentro = hemocentro['id_hemocentro']
                        g.cnpj_hemocentro = cnpj
                        g.nome_hemocentro = hemocentro['nome']
                # adicionar CPF do colaborador se existir
                if usuario.get('cpf'):
                    g.cpf = usuario.get('cpf')
            elif usuario['tipo_usuario'] == 'doador':
                g.cpf = usuario.get('cpf')
        except Exception as e:
            print(f"[ERRO] token_required: {str(e)}")
            return jsonify({
                "success": False,
                "message": "Erro ao validar token"
            }), 401
        return f(current_user, *args, **kwargs)
    return decorated

####################################################################################

# decorator que garante que apenas COLABORADORES podem acessar a rota, verifica token e adiciona dados do hem.
def requer_colaborador(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.get('tipo_usuario') != 'colaborador':
            return jsonify({
                "success": False,
                "message": "Acesso negado. Apenas colaboradores do hemocentro podem realizar esta ação."
            }), 403
        if not hasattr(g, 'id_hemocentro'):
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado ou não vinculado"
            }), 404
        return f(current_user, *args, **kwargs)
    return decorated

 #decorator que garante que apenas DOADORES podem acessar a rota, verifica token e adiciona dados do doador
def requer_doador(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if current_user.get('tipo_usuario') != 'doador':
            return jsonify({
                "success": False,
                "message": "Acesso negado. Apenas doadores podem realizar esta ação."
            }), 403
        return f(current_user, *args, **kwargs)
    return decorated

# compatibilidade (talvez tenha usado isso no codigo sem querer)
hemocentro_required = requer_colaborador

#etc
def validar_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_senha_forte(senha: str) -> bool:
    if len(senha) < 8:
        return False
    if not any(c.isupper() for c in senha):
        return False
    if not any(c.islower() for c in senha):
        return False
    if not any(c.isdigit() for c in senha):
        return False
    return True

def validar_telefone(telefone: str) -> bool:
    num = only_numbers(telefone)
    return len(num) in [10, 11]

def validar_tipo_sanguineo(tipo: str) -> bool:
    tipos_validos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return tipo in tipos_validos

def validar_sexo(sexo: str) -> bool:
    sexos_validos = ['M', 'F', 'm', 'f']
    return sexo in sexos_validos

def obter_usuario_atual():
    if hasattr(g, 'current_user'):
        return g.current_user
    return None

def obter_id_hemocentro():
    if hasattr(g, 'id_hemocentro'):
        return g.id_hemocentro
    return None

def eh_colaborador():
    return hasattr(g, 'tipo_usuario') and g.tipo_usuario == 'colaborador'

def eh_doador():
    return hasattr(g, 'tipo_usuario') and g.tipo_usuario == 'doador'