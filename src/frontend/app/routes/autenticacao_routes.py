from datetime import datetime
from flask import Blueprint, request, jsonify
from models.models import UsuarioModel, HemocentroModel
from utils.auth_utils import (
    only_numbers,
    is_cnpj,
    is_cpf,
    mascara_cpf_cnpj,
    gerar_token,
    token_required,
    validar_email,
    validar_senha_forte,
    validar_telefone,
    validar_sexo
)

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/cadastro', methods=['POST'])
def cadastro():
    try:
        data = request.json or {}
        campos_obrigatorios = ['nome', 'email', 'cpf_cnpj', 'senha', 'telefone', 'tipo_usuario']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({'success': False, 'message': f"Campo obrigatório: {campo}"}), 400
        nome = data['nome'].strip()
        email = data['email'].strip().lower()
        cpf_cnpj = only_numbers(data['cpf_cnpj'])
        senha = data['senha']
        telefone = only_numbers(data['telefone'])
        tipo_usuario = data['tipo_usuario'].lower()
        data_nascimento = data.get('data_nascimento')
        tipo_sanguineo = data.get('tipo_sanguineo')
        sexo = data.get('sexo', '').upper()

        if not validar_email(email):
            return jsonify({'success': False, 'message': 'Email inválido.'}), 400
        if UsuarioModel.buscar_email(email):
            return jsonify({'success': False, 'message': 'Email já cadastrado.'}), 400
        if not validar_senha_forte(senha):
            return jsonify({'success': False, 'message': 'Senha fraca. Deve conter ao menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais.'}), 400
        if not validar_telefone(telefone):
            return jsonify({'success': False, 'message': 'Telefone inválido.'}), 400
        
        if tipo_usuario == 'hemocentro':
            if not is_cnpj(cpf_cnpj):
                return jsonify({'success': False, 'message': 'CNPJ inválido para hemocentro.'}), 400
            hemocentro = HemocentroModel.buscar_por_cnpj(cpf_cnpj)
            if not hemocentro:
                return jsonify({'success': False, 'message': 'CNPJ não autorizado.'}), 403
            if not hemocentro.get('ativo', False):
                return jsonify({'success': False, 'message': 'Hemocentro inativo.'}), 403
        
        elif tipo_usuario == 'doador':
            if not is_cpf(cpf_cnpj):
                return jsonify({'success': False, 'message': 'CPF inválido para doador.'}), 400
            if not data_nascimento:
                return jsonify({'success': False, 'message': 'Data de nascimento é obrigatória para doador.'}), 400
            if not sexo:
                return jsonify({'success': False, 'message': 'Sexo é obrigatório para doador.'}), 400
            if not validar_sexo(sexo):
                return jsonify({'success': False, 'message': 'Sexo inválido. Use M (masculino) ou F (feminino).'}), 400
        else:
            return jsonify({'success': False, 'message': 'Tipo de usuário inválido.'}), 400
        
        if UsuarioModel.buscar_cpf_cnpj(cpf_cnpj):
            return jsonify({'success': False, 'message': 'CPF/CNPJ já cadastrado.'}), 400
        
        usuario_id = UsuarioModel.criar_usuario(
            nome=nome,
            email=email,
            cpf_cnpj=cpf_cnpj,
            senha=senha,
            telefone=telefone,
            tipo_usuario=tipo_usuario,
            data_nascimento=data_nascimento,
            tipo_sanguineo=tipo_sanguineo,
            ativo=True,
        )
        return jsonify({'success': True, 'message':'Cadastro realizado com sucesso! Faça o login para continuar.', 'usuario_id':usuario_id}), 201
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        print(f"Erro no cadastro: {e}")
        return jsonify({'success': False, 'message': 'Erro interno no cadastro.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json or {}
        cpf_cnpj = data.get('cpf_cnpj', '').strip()
        senha = data.get('senha', '')

        # ===== VALIDAÇÃO DE CAMPOS =====
        if not cpf_cnpj or not senha:
            return jsonify({
                "success": False, 
                "message": "CPF/CNPJ e senha são obrigatórios."
            }), 400
        
        # Remove formatação
        cpf_cnpj = only_numbers(cpf_cnpj)
        
        # Valida tamanho (11 CPF ou 14 CNPJ)
        if len(cpf_cnpj) not in [11, 14]:
            return jsonify({
                "success": False,
                "message": "CPF/CNPJ inválido."
            }), 400
        
        # ===== AUTENTICAÇÃO =====
        # MUDANÇA: O método autenticar() agora busca por CPF/CNPJ e valida senha com bcrypt
        usuario = UsuarioModel.autenticar(cpf_cnpj, senha)
        
        if not usuario:
            return jsonify({
                "success": False, 
                "message": "CPF/CNPJ ou senha incorretos."
            }), 401
        
        # ===== VERIFICAÇÃO: USUÁRIO ATIVO =====
        if not usuario.get('ativo', True):
            return jsonify({
                "success": False,
                "message": "Usuário inativo. Entre em contato com o suporte."
            }), 403
        
        # ===== VERIFICAÇÃO ESPECIAL PARA HEMOCENTROS =====
        cnpj_verificado = False
        
        if usuario['tipo_usuario'] == 'hemocentro':
            # SEGURANÇA: Verifica se CNPJ ainda existe e está ativo no banco
            # MOTIVO: Hemocentro pode ter sido desativado após cadastro do usuário
            if not is_cnpj(cpf_cnpj):
                return jsonify({
                    "success": False,
                    "message": "CNPJ inválido para hemocentro."
                }), 403
            
            hemocentro = HemocentroModel.buscar_por_cnpj(cpf_cnpj)
            
            if not hemocentro or not hemocentro.get('ativo', False):
                return jsonify({
                    "success": False,
                    "message": "CNPJ não está mais autorizado. Entre em contato com o administrador."
                }), 403
            
            cnpj_verificado = True  # CNPJ existe e está ativo
        
        # ===== GERAÇÃO DO TOKEN JWT =====
        # MUDANÇA: Substituído session por JWT
        # MOTIVO: JWT é stateless, escalável e funciona com SPA/Mobile
        token = gerar_token(
            usuario_id=usuario['usuario_id'],
            tipo_usuario=usuario['tipo_usuario'],
            nome=usuario['nome'],
            email=usuario['email'],
            cnpj_verificado=cnpj_verificado  # Flag de permissão para hemocentros
        )
        
        # ===== RESPOSTA DE SUCESSO =====
        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso.",
            "token": token,  # NOVO: Token JWT
            "usuario": {
                "usuario_id": usuario['usuario_id'],
                "nome": usuario['nome'],
                "email": usuario['email'],
                "tipo_usuario": usuario['tipo_usuario'],
                "cpf_cnpj_mascarado": mascara_cpf_cnpj(cpf_cnpj),  # NOVO: Segurança LGPD
                "tipo_sanguineo": usuario.get('tipo_sanguineo'),
                "pode_editar": cnpj_verificado  # NOVO: Flag se pode editar (hemocentro)
            }
        }), 200
        
    except Exception as e:
        print(f"Erro no login: {str(e)}")  # Log para debug
        return jsonify({
            "success": False, 
            "message": "Erro interno do servidor."
        }), 500


# ===== ROTA: DADOS DO USUÁRIO AUTENTICADO =====

@auth_bp.route('/me', methods=['GET'])
@token_required  # MUDANÇA: Agora usa JWT ao invés de session
def me(current_user):
    """
    MUDANÇAS:
      1. Renomeado de /status para /me (padrão REST)
      2. Agora usa JWT via decorator @token_required
      3. Corrigido typo: "sucess" → "success"
      4. Busca dados atualizados do banco
    
    MOTIVO: Buscar dados frescos do banco ao invés de confiar apenas no token
    """
    try:
        # Busca dados atualizados do banco
        usuario = UsuarioModel.buscar_id(current_user['usuario_id'])
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado."
            }), 404
        
        # Verifica se é hemocentro e se CNPJ ainda é válido
        pode_editar = False
        if usuario['tipo_usuario'] == 'hemocentro':
            cpf_cnpj = only_numbers(usuario['cpf_cnpj'])
            hemocentro = HemocentroModel.buscar_por_cnpj(cpf_cnpj)
            pode_editar = hemocentro and hemocentro.get('ativo', False)
        
        return jsonify({
            "success": True,  # CORRIGIDO: era "sucess"
            "usuario": {
                "usuario_id": usuario['usuario_id'],
                "nome": usuario['nome'],
                "email": usuario['email'],
                "tipo_usuario": usuario['tipo_usuario'],
                "cpf_cnpj_mascarado": mascara_cpf_cnpj(usuario['cpf_cnpj']),
                "tipo_sanguineo": usuario.get('tipo_sanguineo'),
                "telefone": usuario.get('telefone'),
                "data_nascimento": str(usuario.get('data_nascimento')) if usuario.get('data_nascimento') else None,
                "pode_editar": pode_editar
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar usuário: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== ROTA: REFRESH TOKEN =====

@auth_bp.route('/refresh', methods=['POST'])
@token_required
def refresh_token(current_user):
    """
    NOVO: Gera novo token antes do atual expirar
    MOTIVO: Melhor UX - usuário não precisa fazer login novamente
    
    USO: Frontend chama periodicamente (ex: a cada 20 horas)
    """
    try:
        # Busca dados atualizados
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        
        if not usuario or not usuario.get('ativo', True):
            return jsonify({
                "success": False,
                "message": "Usuário inativo."
            }), 403
        
        # Verifica CNPJ se for hemocentro
        cnpj_verificado = False
        if usuario['tipo_usuario'] == 'hemocentro':
            cpf_cnpj = only_numbers(usuario['cpf_cnpj'])
            hemocentro = HemocentroModel.buscar_por_cnpj(cpf_cnpj)
            cnpj_verificado = hemocentro and hemocentro.get('ativo', False)
        
        # Gera novo token
        novo_token = gerar_token(
            usuario_id=usuario['usuario_id'],
            tipo_usuario=usuario['tipo_usuario'],
            nome=usuario['nome'],
            email=usuario['email'],
            cnpj_verificado=cnpj_verificado
        )
        
        return jsonify({
            "success": True,
            "token": novo_token,
            "message": "Token renovado com sucesso."
        }), 200
        
    except Exception as e:
        print(f"Erro ao renovar token: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== ROTA: VALIDAR TOKEN =====

@auth_bp.route('/validar', methods=['GET'])
@token_required
def validar_token(current_user):
    """
    NOVO: Valida se token ainda é válido
    MOTIVO: Frontend pode verificar antes de fazer requisições importantes
    
    USO: Útil após app ficar em background no mobile
    """
    return jsonify({
        "success": True,
        "message": "Token válido.",
        "usuario_id": current_user['usuario_id'],
        "tipo_usuario": current_user['tipo_usuario']
    }), 200


# ===== ROTA: ALTERAR SENHA =====

@auth_bp.route('/alterar-senha', methods=['PUT'])
@token_required
def alterar_senha(current_user):
    """
    NOVO: Permite usuário alterar própria senha
    MOTIVO: Funcionalidade essencial de segurança
    """
    try:
        data = request.json or {}
        senha_atual = data.get('senha_atual', '')
        senha_nova = data.get('senha_nova', '')
        
        if not senha_atual or not senha_nova:
            return jsonify({
                "success": False,
                "message": "Senha atual e nova senha são obrigatórias."
            }), 400
        
        # Valida força da nova senha
        if not validar_senha_forte(senha_nova):
            return jsonify({
                "success": False,
                "message": "Nova senha fraca. Use no mínimo 8 caracteres com letras maiúsculas, minúsculas e números."
            }), 400
        
        # Busca usuário e verifica senha atual
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado."
            }), 404
        
        # Verifica senha atual
        cpf_cnpj = only_numbers(usuario['cpf_cnpj'])
        if not UsuarioModel.autenticar(cpf_cnpj, senha_atual):
            return jsonify({
                "success": False,
                "message": "Senha atual incorreta."
            }), 401
        
        # Atualiza senha
        UsuarioModel.atualizar_senha(current_user['usuario_id'], senha_nova)
        
        return jsonify({
            "success": True,
            "message": "Senha alterada com sucesso."
        }), 200
        
    except Exception as e:
        print(f"Erro ao alterar senha: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500
