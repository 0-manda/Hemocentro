from flask import Blueprint, request, jsonify, g
from back.utils.auth_utils import (
    token_required, requer_doador, gerar_token, hash_senha, verificar_senha,
    only_numbers, validar_email, validar_senha_forte, validar_telefone,
    validar_tipo_sanguineo, is_cpf, is_cnpj
)
from back.utils.aprovacao_service import criar_solicitacao_aprovacao
from back.models import UsuarioModel, HemocentroModel
from datetime import datetime
from config.config import Config

usuario_bp = Blueprint('usuario_bp', __name__)

# Cadastro de doador
@usuario_bp.route('/cadastrar', methods=['POST'])
def cadastrar_doador():
    """Cadastro de doador - CPF OBRIGATÓRIO"""
    try:
        data = request.json or {}
        campos_obrigatorios = ['nome', 'email', 'senha', 'telefone', 'cpf', 'data_nascimento']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        
        # Limpeza dos dados
        nome = data['nome'].strip()
        email = data['email'].strip().lower()
        senha = data['senha']
        telefone = only_numbers(data['telefone'])
        cpf = only_numbers(data['cpf'])
        tipo_sanguineo = data.get('tipo_sanguineo', '').strip().upper() if data.get('tipo_sanguineo') else None
        
        # Validações
        if len(nome) < 3:
            return jsonify({
                "success": False,
                "message": "Nome deve ter no mínimo 3 caracteres"
            }), 400
        
        if len(nome) > 200:
            return jsonify({
                "success": False,
                "message": "Nome muito longo (máximo 100 caracteres)"
            }), 400
        
        if not validar_email(email):
            return jsonify({
                "success": False,
                "message": "Email inválido"
            }), 400
        
        if UsuarioModel.buscar_por_email(email):
            return jsonify({
                "success": False,
                "message": "Este email já está cadastrado"
            }), 409

        if not validar_senha_forte(senha):
            return jsonify({
                "success": False,
                "message": "Senha deve ter no mínimo 8 caracteres, incluindo maiúsculas, minúsculas e números"
            }), 400

        if not validar_telefone(telefone):
            return jsonify({
                "success": False,
                "message": "Telefone inválido. Use formato: (XX) XXXXX-XXXX"
            }), 400

        if not is_cpf(cpf):
            return jsonify({
                "success": False,
                "message": "CPF inválido"
            }), 400

        if UsuarioModel.buscar_por_cpf(cpf):
            return jsonify({
                "success": False,
                "message": "Este CPF já está cadastrado"
            }), 409
        
        try:
            data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
            idade = (datetime.now().date() - data_nascimento).days // 365
            if idade < 16:
                return jsonify({
                    "success": False,
                    "message": "Você deve ter no mínimo 16 anos para se cadastrar como doador"
                }), 400
            if idade > 120:
                return jsonify({
                    "success": False,
                    "message": "Data de nascimento inválida"
                }), 400
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Formato de data inválido. Use YYYY-MM-DD (ex: 1990-05-20)"
            }), 400
        
        if tipo_sanguineo:
            if not validar_tipo_sanguineo(tipo_sanguineo):
                return jsonify({
                    "success": False,
                    "message": "Tipo sanguíneo inválido. Use: A+, A-, B+, B-, AB+, AB-, O+, O-"
                }), 400
        
        # Criar doador
        senha_hash = hash_senha(senha)
        usuario = UsuarioModel.criar_doador(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            telefone=telefone,
            cpf=cpf,
            data_nascimento=data_nascimento,
            tipo_sanguineo=tipo_sanguineo
        )
        
        return jsonify({
            "success": True,
            "message": "Cadastro realizado com sucesso! Você já pode fazer login e agendar suas doações.",
            "usuario": {
                "id_usuario": usuario['id_usuario'],
                "nome": usuario['nome'],
                "email": usuario['email'],
                "telefone": usuario['telefone'],
                "cpf": usuario['cpf'],
                "tipo_usuario": 'doador',
                "ativo": usuario['ativo'],
                "tipo_sanguineo": usuario.get('tipo_sanguineo'),
                "data_cadastro": usuario['data_cadastro'].isoformat() if usuario.get('data_cadastro') else None
            }
        }), 201
        
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        print(f"[ERRO] Cadastrar doador: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "message": "Erro interno ao cadastrar usuário"
        }), 500


# Cadastro de colaborador
@usuario_bp.route('/cadastrar-colaborador', methods=['POST'])
def cadastrar_colaborador():
    """Cadastro de colaborador - CPF OPCIONAL, CNPJ OBRIGATÓRIO"""
    try:
        data = request.json or {}
        campos_obrigatorios = ['nome', 'email', 'senha', 'telefone', 'cnpj']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        
        # Limpeza dos dados
        nome = data['nome'].strip()
        email = data['email'].strip().lower()
        senha = data['senha']
        telefone = only_numbers(data['telefone'])
        cnpj = only_numbers(data['cnpj'])
        cpf = only_numbers(data.get('cpf', '')) if data.get('cpf') else None  # CPF OPCIONAL
        
        # Validações básicas
        if len(nome) < 3:
            return jsonify({
                "success": False,
                "message": "Nome deve ter no mínimo 3 caracteres"
            }), 400
        
        if len(nome) > 200:
            return jsonify({
                "success": False,
                "message": "Nome muito longo (máximo 200 caracteres)"
            }), 400
        
        if not validar_email(email):
            return jsonify({
                "success": False,
                "message": "Email inválido"
            }), 400
        
        if UsuarioModel.buscar_por_email(email):
            return jsonify({
                "success": False,
                "message": "Este email já está cadastrado"
            }), 409

        if not validar_senha_forte(senha):
            return jsonify({
                "success": False,
                "message": "Senha deve ter no mínimo 8 caracteres, incluindo maiúsculas, minúsculas e números"
            }), 400

        if not validar_telefone(telefone):
            return jsonify({
                "success": False,
                "message": "Telefone inválido. Use formato: (XX) XXXXX-XXXX"
            }), 400

        # Validar CNPJ (obrigatório)
        if not is_cnpj(cnpj):
            return jsonify({
                "success": False,
                "message": "CNPJ inválido"
            }), 400

        # Validar CPF se fornecido (opcional)
        if cpf and not is_cpf(cpf):
            return jsonify({
                "success": False,
                "message": "CPF inválido"
            }), 400

        # Verificar se CPF já está cadastrado (se fornecido)
        if cpf and UsuarioModel.buscar_por_cpf(cpf):
            return jsonify({
                "success": False,
                "message": "Este CPF já está cadastrado"
            }), 409
        
        # Verificar se o hemocentro existe e está ativo
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado. O CNPJ deve corresponder a um hemocentro cadastrado"
            }), 404
        
        if not hemocentro.get('ativo'):
            return jsonify({
                "success": False,
                "message": "Este hemocentro ainda não foi aprovado pelo sistema"
            }), 403
        
        # Criar colaborador (inativo, aguardando aprovação do hemocentro)
        senha_hash = hash_senha(senha)
        usuario = UsuarioModel.criar_colaborador(
            nome=nome,
            email=email,
            senha_hash=senha_hash,
            telefone=telefone,
            cnpj=cnpj,
            cpf=cpf  # CPF opcional
        )
        
        # Enviar email de solicitação de aprovação para o hemocentro
        email_hemocentro = hemocentro.get('email')
        if email_hemocentro:
            dados_solicitacao = {
                'nome': usuario['nome'],
                'email': usuario['email'],
                'telefone': usuario['telefone'],
                'cnpj': usuario['cnpj'],
                'hemocentro_nome': hemocentro['nome']
            }
            
            # Adiciona CPF se fornecido
            if usuario.get('cpf'):
                dados_solicitacao['cpf'] = usuario['cpf']
            
            sucesso_email = criar_solicitacao_aprovacao(
                tipo='colaborador',
                id_entidade=usuario['id_usuario'],
                email_destino=email_hemocentro,
                dados_entidade=dados_solicitacao
            )
            
            if not sucesso_email:
                print(f"[AVISO] Falha ao enviar email de aprovação para {email_hemocentro}")
        else:
            print(f"[AVISO] Hemocentro {hemocentro['nome']} não possui email cadastrado")
        
        # Preparar resposta
        usuario_response = {
            "id_usuario": usuario['id_usuario'],
            "nome": usuario['nome'],
            "email": usuario['email'],
            "telefone": usuario['telefone'],
            "tipo_usuario": 'colaborador',
            "ativo": usuario['ativo'],
            "cnpj": usuario.get('cnpj'),
            "hemocentro": {
                "id_hemocentro": hemocentro['id_hemocentro'],
                "nome": hemocentro['nome'],
                "cnpj": hemocentro['cnpj'],
                "endereco": hemocentro.get('endereco'),
                "cidade": hemocentro.get('cidade'),
                "estado": hemocentro.get('estado')
            },
            "data_cadastro": usuario['data_cadastro'].isoformat() if usuario.get('data_cadastro') else None
        }
        
        # Adicionar CPF se fornecido
        if usuario.get('cpf'):
            usuario_response['cpf'] = usuario['cpf']
        
        return jsonify({
            "success": True,
            "message": "Cadastro realizado com sucesso! Sua solicitação foi enviada para o hemocentro. Você receberá um email quando for aprovado.",
            "usuario": usuario_response
        }), 201
        
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        print(f"[ERRO] Cadastrar colaborador: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "message": "Erro interno ao cadastrar colaborador"
        }), 500


# Login
@usuario_bp.route('/login', methods=['POST'])
def login():
    """
    Login flexível:
    - Doadores: CPF ou Email
    - Colaboradores: CPF, CNPJ ou Email
    """
    try:
        data = request.json or {}
        if not data.get('identificador') or not data.get('senha'):
            return jsonify({
                "success": False,
                "message": "Identificador (email, CPF ou CNPJ) e senha são obrigatórios"
            }), 400
        
        identificador = data['identificador'].strip()
        senha = data['senha']
        usuario = None
        
        # Tentativa 1: Login por EMAIL
        if '@' in identificador:
            email = identificador.lower()
            usuario = UsuarioModel.buscar_por_email(email)
        
        # Tentativa 2: Login por CPF ou CNPJ
        else:
            documento = only_numbers(identificador)
            
            if len(documento) == 11:
                # CPF: pode ser doador ou colaborador
                usuario = UsuarioModel.buscar_por_cpf(documento)
            
            elif len(documento) == 14:
                # CNPJ: busca colaborador
                usuario = UsuarioModel.buscar_por_cnpj(documento)
            
            else:
                return jsonify({
                    "success": False,
                    "message": "Documento inválido. Use CPF (11 dígitos), CNPJ (14 dígitos) ou email"
                }), 400
        
        # Validações de autenticação
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Credenciais incorretas"
            }), 401

        if not usuario.get('ativo', False):
            tipo = usuario.get('tipo_usuario', 'usuário')
            if tipo == 'colaborador':
                return jsonify({
                    "success": False,
                    "message": "Sua conta está aguardando aprovação do hemocentro. Você receberá um email quando for aprovada."
                }), 403
            else:
                return jsonify({
                    "success": False,
                    "message": "Sua conta está inativa. Entre em contato com o suporte."
                }), 403

        if not verificar_senha(senha, usuario['senha']):
            return jsonify({
                "success": False,
                "message": "Credenciais incorretas"
            }), 401

        # Gerar token
        tipo_usuario = usuario.get('tipo_usuario', 'doador')
        token = gerar_token(
            id_usuario=usuario['id_usuario'],
            tipo_usuario=tipo_usuario,
            nome=usuario['nome'],
            email=usuario['email']
        )
        
        # Montar resposta do usuário
        usuario_response = {
            "id_usuario": usuario['id_usuario'],
            "nome": usuario['nome'],
            "email": usuario['email'],
            "telefone": usuario.get('telefone'),
            "tipo_usuario": tipo_usuario
        }
 
        if tipo_usuario == 'doador':
            usuario_response['cpf'] = usuario.get('cpf')
            usuario_response['tipo_sanguineo'] = usuario.get('tipo_sanguineo')
            usuario_response['data_nascimento'] = usuario.get('data_nascimento').isoformat() if usuario.get('data_nascimento') else None
        
        elif tipo_usuario == 'colaborador':
            usuario_response['cnpj'] = usuario.get('cnpj')
            
            # Adicionar CPF se o colaborador tiver
            if usuario.get('cpf'):
                usuario_response['cpf'] = usuario.get('cpf')
            
            # Buscar informações do hemocentro
            cnpj = usuario.get('cnpj')
            if cnpj:
                hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
                if hemocentro:
                    usuario_response['hemocentro'] = {
                        "id_hemocentro": hemocentro['id_hemocentro'],
                        "nome": hemocentro['nome'],
                        "cnpj": hemocentro['cnpj'],
                        "endereco": hemocentro.get('endereco'),
                        "cidade": hemocentro.get('cidade'),
                        "estado": hemocentro.get('estado')
                    }
        
        return jsonify({
            "success": True,
            "message": f"Login realizado com sucesso! Bem-vindo(a), {usuario['nome']}",
            "token": token,
            "usuario": usuario_response
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Login: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao realizar login"
        }), 500


# Perfil
@usuario_bp.route('/perfil', methods=['GET'])
@token_required
def buscar_meu_perfil(current_user):
    try:
        usuario = UsuarioModel.buscar_por_id(g.id_usuario)
        
        if not usuario:
            return jsonify({
                "success": False,
                "message": "Usuário não encontrado"
            }), 404
        
        usuario_safe = {
            "id_usuario": usuario['id_usuario'],
            "nome": usuario['nome'],
            "email": usuario['email'],
            "telefone": usuario.get('telefone'),
            "tipo_usuario": usuario['tipo_usuario'],
            "ativo": usuario.get('ativo'),
            "data_cadastro": usuario.get('data_cadastro').isoformat() if usuario.get('data_cadastro') else None
        }
        
        if g.tipo_usuario == 'doador':
            usuario_safe.update({
                "cpf": usuario.get('cpf'),
                "data_nascimento": usuario.get('data_nascimento').isoformat() if usuario.get('data_nascimento') else None,
                "tipo_sanguineo": usuario.get('tipo_sanguineo')
            })
            
            # Histórico de doações
            from back.models import HistoricoModel  # Adicione este import no topo se não tiver
            
            historico = HistoricoModel.listar_por_usuario(g.id_usuario)
            total_doacoes = len(historico)
            total_ml = sum(d.get('quantidade_ml', 0) for d in historico)
            proxima_doacao = None
            pode_doar = True
            
            if historico:
                doacao_recente = historico[0]
                proxima_doacao = doacao_recente.get('proxima_doacao_permitida')
                
                if proxima_doacao:
                    if isinstance(proxima_doacao, str):
                        proxima_doacao = datetime.strptime(proxima_doacao, '%Y-%m-%d').date()
                    
                    pode_doar = datetime.now().date() >= proxima_doacao
            
            usuario_safe['historico_doacoes'] = {
                "doacoes": historico,
                "estatisticas": {
                    "total_doacoes": total_doacoes,
                    "total_ml": total_ml,
                    "total_litros": round(total_ml / 1000, 2),
                    "proxima_doacao_permitida": str(proxima_doacao) if proxima_doacao else None,
                    "pode_doar_agora": pode_doar
                }
            }
        
        elif g.tipo_usuario == 'colaborador':
            usuario_safe['cnpj'] = usuario.get('cnpj')
            
            if usuario.get('cpf'):
                usuario_safe['cpf'] = usuario.get('cpf')
            
            if hasattr(g, 'hemocentro'):
                usuario_safe['hemocentro'] = {
                    "id_hemocentro": g.hemocentro['id_hemocentro'],
                    "nome": g.hemocentro['nome'],
                    "cnpj": g.hemocentro['cnpj']
                }
        
        return jsonify({
            "success": True,
            "usuario": usuario_safe
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Buscar perfil: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao buscar perfil"
        }), 500


@usuario_bp.route('/perfil', methods=['PUT', 'PATCH'])
@token_required
def atualizar_perfil(current_user):
    try:
        data = request.json or {}
        campos_para_atualizar = {}
        
        if 'nome' in data:
            nome = data['nome'].strip()
            if len(nome) < 3:
                return jsonify({
                    "success": False,
                    "message": "Nome deve ter no mínimo 3 caracteres"
                }), 400
            if len(nome) > 200:
                return jsonify({
                    "success": False,
                    "message": "Nome muito longo (máximo 200 caracteres)"
                }), 400
            campos_para_atualizar['nome'] = nome
        
        if 'telefone' in data:
            telefone = only_numbers(data['telefone'])
            if not validar_telefone(telefone):
                return jsonify({
                    "success": False,
                    "message": "Telefone inválido"
                }), 400
            campos_para_atualizar['telefone'] = telefone
        
        if 'tipo_sanguineo' in data:
            if g.tipo_usuario == 'doador':
                tipo = data['tipo_sanguineo'].strip().upper() if data['tipo_sanguineo'] else None
                if tipo and not validar_tipo_sanguineo(tipo):
                    return jsonify({
                        "success": False,
                        "message": "Tipo sanguíneo inválido"
                    }), 400
                campos_para_atualizar['tipo_sanguineo'] = tipo
            else:
                return jsonify({
                    "success": False,
                    "message": "Colaboradores não podem alterar tipo sanguíneo"
                }), 400
        
        if not campos_para_atualizar:
            return jsonify({
                "success": False,
                "message": "Nenhum campo válido para atualizar"
            }), 400
        
        sucesso = UsuarioModel.atualizar(g.id_usuario, campos_para_atualizar) 
        if not sucesso:
            return jsonify({
                "success": False,
                "message": "Erro ao atualizar perfil"
            }), 500
        
        usuario_atualizado = UsuarioModel.buscar_por_id(g.id_usuario)
        usuario_safe = {
            "id_usuario": usuario_atualizado['id_usuario'],
            "nome": usuario_atualizado['nome'],
            "email": usuario_atualizado['email'],
            "telefone": usuario_atualizado.get('telefone'),
            "tipo_usuario": usuario_atualizado['tipo_usuario']
        }
        
        if g.tipo_usuario == 'doador':
            usuario_safe['tipo_sanguineo'] = usuario_atualizado.get('tipo_sanguineo')
        elif g.tipo_usuario == 'colaborador':
            if usuario_atualizado.get('cpf'):
                usuario_safe['cpf'] = usuario_atualizado.get('cpf')
        
        return jsonify({
            "success": True,
            "message": "Perfil atualizado com sucesso",
            "usuario": usuario_safe
        }), 200

    except Exception as e:
        print(f"[ERRO] Atualizar perfil: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao atualizar perfil"
        }), 500


@usuario_bp.route('/alterar-senha', methods=['POST'])
@token_required
def alterar_senha(current_user):
    try:
        data = request.json or {}
        if not data.get('senha_atual') or not data.get('senha_nova'):
            return jsonify({
                "success": False,
                "message": "Senha atual e nova senha são obrigatórias"
            }), 400
        
        usuario = UsuarioModel.buscar_por_id(g.id_usuario)
        if not verificar_senha(data['senha_atual'], usuario['senha']):
            return jsonify({
                "success": False,
                "message": "Senha atual incorreta"
            }), 401
        
        senha_nova = data['senha_nova']
        if not validar_senha_forte(senha_nova):
            return jsonify({
                "success": False,
                "message": "Senha deve ter no mínimo 8 caracteres, incluindo maiúsculas, minúsculas e números"
            }), 400
        
        if verificar_senha(senha_nova, usuario['senha']):
            return jsonify({
                "success": False,
                "message": "Nova senha deve ser diferente da senha atual"
            }), 400
        
        senha_hash = hash_senha(senha_nova)
        sucesso = UsuarioModel.atualizar(g.id_usuario, {'senha': senha_hash})
        if not sucesso:
            return jsonify({
                "success": False,
                "message": "Erro ao alterar senha"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "Senha alterada com sucesso"
        }), 200

    except Exception as e:
        print(f"[ERRO] Alterar senha: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao alterar senha"
        }), 500


@usuario_bp.route('/validar-token', methods=['GET'])
@token_required
def validar_token_route(current_user):
    return jsonify({
        "success": True,
        "message": "Token válido",
        "usuario": {
            "id_usuario": g.id_usuario,
            "tipo_usuario": g.tipo_usuario,
            "nome": g.nome,
            "email": g.email
        }
    }), 200