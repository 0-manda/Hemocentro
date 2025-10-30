import re
import jwt
import os
import bcrypt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from models.models import UsuarioModel
from dotenv import load_dotenv

load_dotenv()

# ============== JWT SETTINGS ==============
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'MUDE-ESTA-CHAVE-SECRETA-EM-PRODUCAO')
ALGORITHM = 'HS256'
TOKEN_EXPIRATION_HOURS = 24

# ============== VALIDAR CPF/CNPJ ==============
def only_numbers(value: str) -> str:
    """Remove todos os caracteres não numéricos"""
    return re.sub(r'\D', '', value or '')

def is_cnpj(value: str) -> bool:
    """Valida CNPJ usando algoritmo de dígitos verificadores"""
    c = only_numbers(value)
    if len(c) != 14 or c == c[0] * 14:
        return False
    
    def calc_digit(digs):
        s = 0
        peso = len(digs) - 7
        for ch in digs:
            s += int(ch) * peso
            peso -= 1
            if peso < 2:
                peso = 9
        res = 11 - (s % 11)
        return '0' if res >= 10 else str(res)
    
    return c[-2:] == calc_digit(c[:12]) + calc_digit(c[:12] + calc_digit(c[:12]))

def is_cpf(value: str) -> bool:
    """Valida CPF usando algoritmo de dígitos verificadores"""
    p = only_numbers(value)
    if len(p) != 11 or p == p[0] * 11:
        return False
    
    def calc_digit(digs):
        s = 0
        peso = len(digs) + 1
        for ch in digs:
            s += int(ch) * peso
            peso -= 1
        res = 11 - (s % 11)
        return '0' if res >= 10 else str(res)
    
    return p[-2:] == calc_digit(p[:9]) + calc_digit(p[:9] + calc_digit(p[:9]))

def mascara_cpf_cnpj(cpf_cnpj: str) -> str:
    """Retorna CPF/CNPJ mascarado para exibição"""
    num = only_numbers(cpf_cnpj)
    if len(num) == 11:
        return f"***.***{num[6:9]}-{num[9:]}"
    elif len(num) == 14:
        return f"**.***.***/0001-{num[10:]}"
    return "***"

# ============== HASH DE SENHA COM BCRYPT ==============
def hash_senha(senha: str) -> str:
    """Gera hash seguro da senha usando bcrypt"""
    return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Verifica se a senha corresponde ao hash bcrypt"""
    return bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8'))

# ============== JWT ==============
def gerar_token(usuario_id: int, tipo_usuario: str, nome: str, email: str, cnpj_verificado: bool = False) -> str:
    """Gera token JWT com informações do usuário"""
    payload = {
        'usuario_id': usuario_id,
        'tipo_usuario': tipo_usuario,
        'nome': nome,
        'email': email,
        'cnpj_verificado': cnpj_verificado,
        'exp': datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRATION_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str):
    """Verifica e decodifica token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# ============== DECORATORS ==============
def token_required(f):
    """Decorator para rotas que requerem autenticação"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"success": False, "message": "Token inválido."}), 401
        
        if not token:
            return jsonify({"success": False, "message": "Token não fornecido, faça login."}), 401
        
        current_user = verificar_token(token)
        if not current_user:
            return jsonify({"success": False, "message": "Token inválido ou expirado."}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def hemocentro_required(f):
    """Decorator para rotas que requerem permissão de hemocentro"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('tipo_usuario') != 'hemocentro':
            return jsonify({"success": False, "message": "Acesso negado. Apenas hemocentros."}), 403
        
        if not current_user.get('cnpj_verificado', False):
            return jsonify({"success": False, "message": "CNPJ não verificado."}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator para rotas que requerem permissão de administrador"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.get('tipo_usuario') != 'admin':
            return jsonify({"success": False, "message": "Acesso negado. Apenas administradores."}), 403
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# ============== VALIDAÇÕES AUXILIARES ==============
def validar_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_senha_forte(senha: str) -> bool:
    """Valida se senha tem no mínimo 8 caracteres com maiúsculas, minúsculas e números"""
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
    """Valida telefone brasileiro (10 ou 11 dígitos)"""
    num = only_numbers(telefone)
    return len(num) in [10, 11]

def validar_tipo_sanguineo(tipo: str) -> bool:
    """Valida tipo sanguíneo"""
    tipos_validos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return tipo in tipos_validos

def validar_sexo(sexo: str) -> bool:
    """Valida sexo (M ou F)"""
    sexos_validos = ['M', 'F', 'm', 'f']
    return sexo in sexos_validos