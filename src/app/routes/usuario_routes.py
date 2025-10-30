from flask import Blueprint, request, jsonify
from utils.auth_utils import token_required, gerar_token, hash_senha, verificar_senha
from models.models import UsuarioModel
import re
from datetime import datetime, timedelta

usuario_bp = Blueprint('usuario_bp', __name__)

# ============== CADASTRAR USUÁRIO (Público) ==============
@usuario_bp.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    """
    Cadastra um novo usuário no sistema
    Rota pública - não requer autenticação
    """
    try:
        data = request.json
        
        # ===== VALIDAÇÃO: Campos obrigatórios =====
        campos_obrigatorios = ['nome', 'email', 'cpf', 'senha', 'telefone', 'data_nascimento', 'sexo']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        
        # ===== VALIDAÇÃO: Email =====
        email = data['email'].lower().strip()
        regex_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(regex_email, email):
            return jsonify({
                "success": False,
                "message": "Email inválido"
            }), 400
        
        # Verificar se email já existe
        if UsuarioModel.buscar_por_email(email):
            return jsonify({
                "success": False,
                "message": "Este email já está cadastrado"
            }), 409
        
        # ===== VALIDAÇÃO: CPF =====
        cpf = re.sub(r'\D', '', data['cpf'])  # Remove caracteres não numéricos
        
        if len(cpf) != 11:
            return jsonify({
                "success": False,
                "message": "CPF deve ter 11 dígitos"
            }), 400
        
        # Validação básica de CPF (algoritmo completo deve estar em utils)
        if not validar_cpf(cpf):
            return jsonify({
                "success": False,
                "message": "CPF inválido"
            }), 400
        
        # Verificar se CPF já existe
        if UsuarioModel.buscar_por_cpf(cpf):
            return jsonify({
                "success": False,
                "message": "Este CPF já está cadastrado"
            }), 409
        
        # ===== VALIDAÇÃO: Senha =====
        senha = data['senha']
        if len(senha) < 8:
            return jsonify({
                "success": False,
                "message": "Senha deve ter no mínimo 8 caracteres"
            }), 400
        
        # Verificar força da senha
        if not re.search(r'[A-Z]', senha):
            return jsonify({
                "success": False,
                "message": "Senha deve conter pelo menos uma letra maiúscula"
            }), 400
        
        if not re.search(r'[a-z]', senha):
            return jsonify({
                "success": False,
                "message": "Senha deve conter pelo menos uma letra minúscula"
            }), 400
        
        if not re.search(r'\d', senha):
            return jsonify({
                "success": False,
                "message": "Senha deve conter pelo menos um número"
            }), 400
        
        # ===== VALIDAÇÃO: Telefone =====
        telefone = re.sub(r'\D', '', data['telefone'])
        if len(telefone) < 10 or len(telefone) > 11:
            return jsonify({
                "success": False,
                "message": "Telefone inválido. Use formato: (XX) XXXXX-XXXX"
            }), 400
        
        # ===== VALIDAÇÃO: Data de Nascimento (idade mínima 16 anos) =====
        try:
            data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d')
            idade = (datetime.now() - data_nascimento).days // 365
            
            if idade < 16:
                return jsonify({
                    "success": False,
                    "message": "Você deve ter no mínimo 16 anos para se cadastrar"
                }), 400
            
            if idade > 120:
                return jsonify({
                    "success": False,
                    "message": "Data de nascimento inválida"
                }), 400
                
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Formato de data inválido. Use YYYY-MM-DD"
            }), 400
        
        # ===== VALIDAÇÃO: Sexo =====
        sexo = data['sexo'].upper()
        if sexo not in ['M', 'F', 'O']:
            return jsonify({
                "success": False,
                "message": "Sexo deve ser M (Masculino), F (Feminino) ou O (Outro)"
            }), 400
        
        # ===== VALIDAÇÃO: Tipo Sanguíneo (opcional) =====
        tipo_sanguineo = data.get('tipo_sanguineo')
        if tipo_sanguineo:
            tipos_validos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            if tipo_sanguineo not in tipos_validos:
                return jsonify({
                    "success": False,
                    "message": f"Tipo sanguíneo inválido. Valores aceitos: {', '.join(tipos_validos)}"
                }), 400
        
        # ===== CRIAR USUÁRIO =====
        senha_hash = hash_senha(senha)
        
        usuario = UsuarioModel.criar(
            nome=data['nome'].strip(),
            email=email,
            cpf=cpf,
            senha_hash=senha_hash,
            telefone=telefone,
            data_nascimento=data['data_nascimento'],
            sexo=sexo,
            tipo_sanguineo=tipo_sanguineo,
            endereco=data.get('endereco'),
            cidade=data.get('cidade'),
            estado=data.get('estado'),
            cep=data.get('cep')
            # tipo_usuario='doador' por padrão
            # ativo=True por padrão
            # data_cadastro=NOW() automático
        )
        
        # Gerar token de autenticação
        token = gerar_token(usuario['id'])
        
        # Remover dados sensíveis antes de retornar
        usuario_response = {
            "id": usuario['id'],
            "nome": usuario['nome'],
            "email": usuario['email'],
            "telefone": usuario['telefone'],
            "tipo_sanguineo": usuario.get('tipo_sanguineo'),
            "data_cadastro": usuario['data_cadastro']
        }
        
        return jsonify({
            "success": True,
            "message": "Usuário cadastrado com sucesso",
            "usuario": usuario_response,
            "token": token
        }), 201
        
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        print(f"[ERRO] Cadastrar usuário: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "Erro interno ao cadastrar usuário"
        }), 500


# ============== LOGIN ==============
@usuario_bp.route('/login', methods=['POST'])
def login():
    """
    Autentica um usuário e retorna token JWT
    """
    try:
        data = request.json
        
        # Validar campos
        if not data.get('email') or not data.get('senha'):
            return jsonify({
                "success": False,
                "message": "Email e senha são obrigatórios"
            }), 400
        
        email = data['email'].lower().strip()
        senha = data['senha']
        
        # Buscar usuário
        usuario = UsuarioModel.buscar_por_email(email)
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Email ou senha incorretos"
            }), 401
        
        # Verificar se usuário está ativo
        if not usuario['ativo']:
            return jsonify({
                "success": False,
                "message": "Usuário inativo. Entre em contato com o suporte."
            }), 403
        
        # Verificar senha
        if not verificar_senha(senha, usuario['senha_hash']):
            return jsonify({
                "success": False,
                "message": "Email ou senha incorretos"
            }), 401
        
        # Atualizar último login
        UsuarioModel.atualizar_ultimo_login(usuario['id'])
        
        # Gerar token
        token = gerar_token(usuario['id'])
        
        # Dados do usuário (sem informações sensíveis)
        usuario_response = {
            "id": usuario['id'],
            "nome": usuario['nome'],
            "email": usuario['email'],
            "telefone": usuario['telefone'],
            "tipo_sanguineo": usuario.get('tipo_sanguineo'),
            "tipo_usuario": usuario.get('tipo_usuario', 'doador')
        }
        
        return jsonify({
            "success": True,
            "message": "Login realizado com sucesso",
            "token": token,
            "usuario": usuario_response
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Login: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao realizar login"
        }), 500


# ============== BUSCAR MEU PERFIL ==============
@usuario_bp.route('/meu_perfil', methods=['GET'])
@token_required
def buscar_meu_perfil(usuario_atual):
    """
    Retorna informações do perfil do usuário autenticado
    """
    try:
        usuario = UsuarioModel.buscar_por_id(usuario_atual['id'])
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado"
            }), 404
        
        # Remover dados sensíveis
        del usuario['senha_hash']
        
        return jsonify({
            "success": True,
            "usuario": usuario
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Buscar perfil: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao buscar perfil"
        }), 500


# ============== ATUALIZAR PERFIL ==============
@usuario_bp.route('/atualizar_perfil', methods=['PUT', 'PATCH'])
@token_required
def atualizar_perfil(usuario_atual):
    """
    Atualiza informações do perfil do usuário
    Campos sensíveis (email, CPF) requerem verificação adicional
    """
    try:
        data = request.json
        
        # Campos que podem ser atualizados
        campos_editaveis = ['nome', 'telefone', 'tipo_sanguineo', 'endereco', 
                           'cidade', 'estado', 'cep', 'data_nascimento']
        dados_atualizacao = {}
        
        # Validar e preparar campos para atualização
        if 'nome' in data:
            if len(data['nome'].strip()) < 3:
                return jsonify({
                    "success": False,
                    "message": "Nome deve ter no mínimo 3 caracteres"
                }), 400
            dados_atualizacao['nome'] = data['nome'].strip()
        
        if 'telefone' in data:
            telefone = re.sub(r'\D', '', data['telefone'])
            if len(telefone) < 10 or len(telefone) > 11:
                return jsonify({
                    "success": False,
                    "message": "Telefone inválido"
                }), 400
            dados_atualizacao['telefone'] = telefone
        
        if 'tipo_sanguineo' in data:
            tipos_validos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            if data['tipo_sanguineo'] and data['tipo_sanguineo'] not in tipos_validos:
                return jsonify({
                    "success": False,
                    "message": "Tipo sanguíneo inválido"
                }), 400
            dados_atualizacao['tipo_sanguineo'] = data['tipo_sanguineo']
        
        # Adicionar outros campos editáveis
        for campo in ['endereco', 'cidade', 'estado', 'cep']:
            if campo in data:
                dados_atualizacao[campo] = data[campo]
        
        if not dados_atualizacao:
            return jsonify({
                "success": False,
                "message": "Nenhum campo válido para atualizar"
            }), 400
        
        # Atualizar usuário
        usuario_atualizado = UsuarioModel.atualizar(usuario_atual['id'], dados_atualizacao)
        
        # Remover dados sensíveis
        del usuario_atualizado['senha_hash']
        
        return jsonify({
            "success": True,
            "message": "Perfil atualizado com sucesso",
            "usuario": usuario_atualizado
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Atualizar perfil: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao atualizar perfil"
        }), 500


# ============== ALTERAR SENHA ==============
@usuario_bp.route('/alterar_senha', methods=['POST'])
@token_required
def alterar_senha(usuario_atual):
    """
    Altera a senha do usuário
    Requer senha atual para confirmação
    """
    try:
        data = request.json
        
        # Validar campos
        if not data.get('senha_atual') or not data.get('senha_nova'):
            return jsonify({
                "success": False,
                "message": "Senha atual e nova senha são obrigatórias"
            }), 400
        
        # Buscar usuário completo
        usuario = UsuarioModel.buscar_por_id(usuario_atual['id'])
        
        # Verificar senha atual
        if not verificar_senha(data['senha_atual'], usuario['senha_hash']):
            return jsonify({
                "success": False,
                "message": "Senha atual incorreta"
            }), 401
        
        # Validar nova senha
        senha_nova = data['senha_nova']
        if len(senha_nova) < 8:
            return jsonify({
                "success": False,
                "message": "Nova senha deve ter no mínimo 8 caracteres"
            }), 400
        
        if not re.search(r'[A-Z]', senha_nova) or not re.search(r'[a-z]', senha_nova) or not re.search(r'\d', senha_nova):
            return jsonify({
                "success": False,
                "message": "Senha deve conter letras maiúsculas, minúsculas e números"
            }), 400
        
        # Verificar se nova senha é diferente da atual
        if verificar_senha(senha_nova, usuario['senha_hash']):
            return jsonify({
                "success": False,
                "message": "Nova senha deve ser diferente da senha atual"
            }), 400
        
        # Atualizar senha
        senha_hash = hash_senha(senha_nova)
        UsuarioModel.atualizar_senha(usuario_atual['id'], senha_hash)
        
        return jsonify({
            "success": True,
            "message": "Senha alterada com sucesso"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Alterar senha: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao alterar senha"
        }), 500


# ============== SOLICITAR RECUPERAÇÃO DE SENHA ==============
@usuario_bp.route('/recuperar_senha', methods=['POST'])
def solicitar_recuperacao_senha():
    """
    Envia email com código de recuperação de senha
    """
    try:
        data = request.json
        
        if not data.get('email'):
            return jsonify({
                "success": False,
                "message": "Email é obrigatório"
            }), 400
        
        email = data['email'].lower().strip()
        usuario = UsuarioModel.buscar_por_email(email)
        
        # Por segurança, sempre retornar sucesso mesmo se email não existir
        if not usuario:
            return jsonify({
                "success": True,
                "message": "Se o email existir, você receberá instruções de recuperação"
            }), 200
        
        # Gerar código de recuperação
        codigo = UsuarioModel.gerar_codigo_recuperacao(usuario['id'])
        
        # TODO: Enviar email com código
        # enviar_email_recuperacao(email, codigo)
        
        return jsonify({
            "success": True,
            "message": "Se o email existir, você receberá instruções de recuperação"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Recuperar senha: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao processar recuperação de senha"
        }), 500


# ============== REDEFINIR SENHA COM CÓDIGO ==============
@usuario_bp.route('/redefinir_senha', methods=['POST'])
def redefinir_senha():
    """
    Redefine senha usando código de recuperação
    """
    try:
        data = request.json
        
        if not data.get('email') or not data.get('codigo') or not data.get('senha_nova'):
            return jsonify({
                "success": False,
                "message": "Email, código e nova senha são obrigatórios"
            }), 400
        
        email = data['email'].lower().strip()
        codigo = data['codigo']
        senha_nova = data['senha_nova']
        
        # Validar nova senha
        if len(senha_nova) < 8:
            return jsonify({
                "success": False,
                "message": "Senha deve ter no mínimo 8 caracteres"
            }), 400
        
        # Verificar código
        if not UsuarioModel.verificar_codigo_recuperacao(email, codigo):
            return jsonify({
                "success": False,
                "message": "Código inválido ou expirado"
            }), 401
        
        # Buscar usuário e atualizar senha
        usuario = UsuarioModel.buscar_por_email(email)
        senha_hash = hash_senha(senha_nova)
        UsuarioModel.atualizar_senha(usuario['id'], senha_hash)
        
        # Invalidar código usado
        UsuarioModel.invalidar_codigo_recuperacao(usuario['id'])
        
        return jsonify({
            "success": True,
            "message": "Senha redefinida com sucesso"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Redefinir senha: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao redefinir senha"
        }), 500


# ============== DESATIVAR CONTA ==============
@usuario_bp.route('/desativar_conta', methods=['DELETE'])
@token_required
def desativar_conta(usuario_atual):
    """
    Desativa a conta do usuário (soft delete)
    Requer confirmação de senha
    """
    try:
        data = request.json
        
        if not data.get('senha'):
            return jsonify({
                "success": False,
                "message": "Senha é obrigatória para desativar a conta"
            }), 400
        
        # Buscar usuário completo
        usuario = UsuarioModel.buscar_por_id(usuario_atual['id'])
        
        # Verificar senha
        if not verificar_senha(data['senha'], usuario['senha_hash']):
            return jsonify({
                "success": False,
                "message": "Senha incorreta"
            }), 401
        
        # Desativar conta
        UsuarioModel.desativar(usuario_atual['id'])
        
        return jsonify({
            "success": True,
            "message": "Conta desativada com sucesso"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Desativar conta: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao desativar conta"
        }), 500


# ============== HISTÓRICO DE DOAÇÕES ==============
@usuario_bp.route('/meu_historico_doacoes', methods=['GET'])
@token_required
def buscar_historico_doacoes(usuario_atual):
    """
    Retorna histórico completo de doações do usuário
    """
    try:
        historico = UsuarioModel.buscar_historico_doacoes(usuario_atual['id'])
        
        return jsonify({
            "success": True,
            "total_doacoes": len(historico),
            "historico": historico
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Buscar histórico: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao buscar histórico de doações"
        }), 500


# ============== VALIDAR CPF (Função auxiliar) ==============
def validar_cpf(cpf):
    """
    Valida CPF usando algoritmo de dígitos verificadores
    """
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Validar primeiro dígito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10 % 11) % 10
    
    if int(cpf[9]) != digito1:
        return False
    
    # Validar segundo dígito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10 % 11) % 10
    
    return int(cpf[10]) == digito2