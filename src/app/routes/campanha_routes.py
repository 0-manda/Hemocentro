from flask import Blueprint, request, jsonify
from models.models import CampanhaModel, HemocentroModel, UsuarioModel
from utils.auth_utils import hemocentro_required, token_required, only_numbers, validar_tipo_sanguineo
from datetime import datetime

campanha_bp = Blueprint('campanha_bp', __name__)

@campanha_bp.route('/cadastrar_campanha', methods=['POST'])
@token_required
@hemocentro_required
def criar_campanha(current_user):
    try:
        data = request.json or {}
        campos_necessarios = ['id_hemocentro', 'nome', 'descricao', 'data_inicio', 'data_fim', 'tipo_sanguineo_necessario', 'quantidade_meta', 'quantidade_atual', 'objetivo_campanha', 'ativa', 'destaque', 'data_criacao']
        for campo in campos_necessarios:
            if campo not in data or not data.get(campo):
                return jsonify({"success": False, "message": f"Campo obrigatório faltando: {campo}" }), 400
        tipos_validos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        tipo_sanguineo = data['tipo_sanguineo_necessario'].strip().upper()
        if tipo_sanguineo not in tipos_validos:
            return jsonify({"success": False, "message": f"Tipo sanguíneo inválido: {tipo_sanguineo}"}), 400
        try:
            data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d')
            data_fim = datetime.strptime(data['data_fim'], '%Y-%m-%d')
            if data_fim <= data_inicio:
                return jsonify({"success": False, "message": "Data de fim deve ser posterior à data de início."}), 400

        except ValueError:
            return jsonify({"success": False, "message": "Formato de data inválido. Use 'YYYY-MM-DD'."}), 400
        try:
            quantidade_meta = int(data['quantidade_meta'])
            if quantidade_meta <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "Quantidade meta deve ser um número inteiro positivo."}), 400
        
        usuario_id = current_user['usuario_id']
        usuario = UsuarioModel.buscar_por_id(usuario_id)
        if not usuario :
            return jsonify({"success": False, "message": "Usuário não encontrado."}), 404
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        if not hemocentro:
            return jsonify({"success": False, "message": "Hemocentro não encontrado."}), 404
        hemocentro_id = hemocentro['hemocentro_id']
        if 'hemocentro_id' in data and data['hemocentro_id'] != hemocentro_id:
            return jsonify({"success": False, "message": "Você não tem permissão para criar campanhas para este hemocentro."}), 403
        
        campanha = CampanhaModel.criar_campanha(
            hemocentro_id=hemocentro_id,
            nome=data['nome'].strip(),
            descricao=data['descricao'].strip(),
            data_inicio=data['data_inicio'],
            data_fim=data['data_fim'],
            tipo_sanguineo_necessario=tipo_sanguineo,
            quantidade_meta=quantidade_meta,
            quantidade_atual=0,
            objetivo_campanha=data['objetivo_campanha'].strip(),
            ativa=True,
            destaque=data.get('destaque', False),
            data_criacao=datetime.now().strftime('%Y-%m-%d')
        )
        return jsonify({
            "success": True,
            "message": "Campanha criada com sucesso!",
            "campanha": campanha
        }), 201
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": f"Erro de validação: {str(e)}"
        }), 400
    except Exception as e:
        print(f"Erro ao criar campanha: {str(e)}")  # Log para debug
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== LISTAR CAMPANHAS ATIVAS (PÚBLICO) =====

@campanha_bp.route('/campanhas', methods=['GET'])
def listar_campanhas():
    """
    NOVO: Lista campanhas ativas
    MOTIVO: Doadores precisam ver campanhas disponíveis
    
    Filtros opcionais via query params:
      - ?hemocentro_id=1
      - ?tipo_sanguineo=O+
      - ?destaque=true
    """
    try:
        # Parâmetros de filtro
        hemocentro_id = request.args.get('hemocentro_id', type=int)
        tipo_sanguineo = request.args.get('tipo_sanguineo')
        apenas_destaque = request.args.get('destaque', 'false').lower() == 'true'
        
        # Busca campanhas
        campanhas = CampanhaModel.listar_ativas(
            hemocentro_id=hemocentro_id,
            tipo_sanguineo=tipo_sanguineo,
            apenas_destaque=apenas_destaque
        )
        
        return jsonify({
            "success": True,
            "campanhas": campanhas,
            "total": len(campanhas)
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar campanhas: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== BUSCAR CAMPANHA POR ID (PÚBLICO) =====

@campanha_bp.route('/campanhas/<int:campanha_id>', methods=['GET'])
def buscar_campanha(campanha_id):
    """
    NOVO: Busca detalhes de uma campanha específica
    MOTIVO: Página de detalhes da campanha
    """
    try:
        campanha = CampanhaModel.buscar_por_id(campanha_id)
        
        if not campanha:
            return jsonify({
                "success": False,
                "message": "Campanha não encontrada."
            }), 404
        
        return jsonify({
            "success": True,
            "campanha": campanha
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar campanha: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== ATUALIZAR CAMPANHA =====

@campanha_bp.route('/campanhas/<int:campanha_id>', methods=['PUT'])
@token_required
@hemocentro_required
def atualizar_campanha(current_user, campanha_id):
    """
    NOVO: Atualiza campanha existente
    MOTIVO: Hemocentro precisa editar suas campanhas
    
    SEGURANÇA: Só pode editar campanhas do próprio hemocentro
    """
    try:
        data = request.json or {}
        
        # Busca campanha
        campanha = CampanhaModel.buscar_por_id(campanha_id)
        
        if not campanha:
            return jsonify({
                "success": False,
                "message": "Campanha não encontrada."
            }), 404
        
        # SEGURANÇA: Verifica se campanha pertence ao hemocentro do usuário
        from models.models import UsuarioModel
        from utils.auth_utils import only_numbers
        
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        
        if campanha['hemocentro_id'] != hemocentro['hemocentro_id']:
            return jsonify({
                "success": False,
                "message": "Você só pode editar campanhas do seu hemocentro."
            }), 403
        
        # Campos editáveis
        campos_editaveis = {
            'nome': data.get('nome'),
            'descricao': data.get('descricao'),
            'data_fim': data.get('data_fim'),
            'tipo_sanguineo_necessario': data.get('tipo_sanguineo_necessario'),
            'quantidade_meta': data.get('quantidade_meta'),
            'objetivo_campanha': data.get('objetivo_campanha'),
            'ativa': data.get('ativa'),
            'destaque': data.get('destaque')
        }
        
        # Remove campos None (não enviados)
        campos_para_atualizar = {k: v for k, v in campos_editaveis.items() if v is not None}
        
        if not campos_para_atualizar:
            return jsonify({
                "success": False,
                "message": "Nenhum campo para atualizar."
            }), 400
        
        # Validações específicas
        if 'tipo_sanguineo_necessario' in campos_para_atualizar:
            tipos_validos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-', 'Todos']
            tipo = campos_para_atualizar['tipo_sanguineo_necessario'].strip().upper()
            if tipo not in tipos_validos:
                return jsonify({
                    "success": False,
                    "message": f"Tipo sanguíneo inválido. Use: {', '.join(tipos_validos)}"
                }), 400
            campos_para_atualizar['tipo_sanguineo_necessario'] = tipo
        
        if 'data_fim' in campos_para_atualizar:
            try:
                data_fim = datetime.strptime(campos_para_atualizar['data_fim'], '%Y-%m-%d')
                data_inicio = datetime.strptime(campanha['data_inicio'], '%Y-%m-%d')
                
                if data_fim <= data_inicio:
                    return jsonify({
                        "success": False,
                        "message": "Data de término deve ser posterior à data de início."
                    }), 400
            except ValueError:
                return jsonify({
                    "success": False,
                    "message": "Formato de data inválido. Use: YYYY-MM-DD"
                }), 400
        
        # Atualiza campanha
        CampanhaModel.atualizar(campanha_id, campos_para_atualizar)
        
        return jsonify({
            "success": True,
            "message": "Campanha atualizada com sucesso!"
        }), 200
        
    except Exception as e:
        print(f"Erro ao atualizar campanha: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== DELETAR/DESATIVAR CAMPANHA =====

@campanha_bp.route('/campanhas/<int:campanha_id>', methods=['DELETE'])
@token_required
@hemocentro_required
def desativar_campanha(current_user, campanha_id):
    """
    NOVO: Desativa campanha (soft delete)
    MOTIVO: Não deletar permanentemente (preservar histórico)
    
    SEGURANÇA: Só pode desativar campanhas do próprio hemocentro
    """
    try:
        # Busca campanha
        campanha = CampanhaModel.buscar_por_id(campanha_id)
        
        if not campanha:
            return jsonify({
                "success": False,
                "message": "Campanha não encontrada."
            }), 404
        
        # SEGURANÇA: Verifica permissão
        from models.models import UsuarioModel
        from utils.auth_utils import only_numbers
        
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        
        if campanha['hemocentro_id'] != hemocentro['hemocentro_id']:
            return jsonify({
                "success": False,
                "message": "Você só pode desativar campanhas do seu hemocentro."
            }), 403
        
        # Desativa (soft delete)
        CampanhaModel.desativar(campanha_id)
        
        return jsonify({
            "success": True,
            "message": "Campanha desativada com sucesso!"
        }), 200
        
    except Exception as e:
        print(f"Erro ao desativar campanha: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== LISTAR CAMPANHAS DO HEMOCENTRO =====

@campanha_bp.route('/minhas-campanhas', methods=['GET'])
@token_required
@hemocentro_required
def minhas_campanhas(current_user):
    """
    NOVO: Lista todas as campanhas do hemocentro logado
    MOTIVO: Dashboard do hemocentro
    """
    try:
        # Busca hemocentro do usuário
        from models.models import UsuarioModel
        from utils.auth_utils import only_numbers
        
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado."
            }), 404
        
        # Lista campanhas (ativas e inativas)
        campanhas = CampanhaModel.listar_por_hemocentro(hemocentro['hemocentro_id'])
        
        return jsonify({
            "success": True,
            "campanhas": campanhas,
            "total": len(campanhas)
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar minhas campanhas: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500
    
    