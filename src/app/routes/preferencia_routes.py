from flask import Blueprint, request, jsonify
from utils.auth_utils import token_required
from models.models import PreferenciaModel, UsuarioModel

preferencia_bp = Blueprint('preferencia_bp', __name__)

# ============== CRIAR/ATUALIZAR PREFERÊNCIAS ==============
@preferencia_bp.route('/minhas_preferencias', methods=['POST', 'PUT'])
@token_required
def salvar_preferencias(current_user):

    try:
        data = request.json
        
        # ===== VALIDAÇÃO: Campos obrigatórios =====
        campos_obrigatorios = ['dias_preferencia', 'periodos_preferencia']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        
        # ===== VALIDAÇÃO: Dias da semana =====
        dias_validos = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
        dias_preferencia = data['dias_preferencia']
        
        if not isinstance(dias_preferencia, list) or len(dias_preferencia) == 0:
            return jsonify({
                "success": False,
                "message": "dias_preferencia deve ser uma lista com pelo menos um dia"
            }), 400
        
        for dia in dias_preferencia:
            if dia.lower() not in dias_validos:
                return jsonify({
                    "success": False,
                    "message": f"Dia inválido: '{dia}'. Valores aceitos: {', '.join(dias_validos)}"
                }), 400
        
        # ===== VALIDAÇÃO: Períodos do dia =====
        periodos_validos = ['manha', 'tarde', 'noite']
        periodos_preferencia = data['periodos_preferencia']
        
        if not isinstance(periodos_preferencia, list) or len(periodos_preferencia) == 0:
            return jsonify({
                "success": False,
                "message": "periodos_preferencia deve ser uma lista com pelo menos um período"
            }), 400
        
        for periodo in periodos_preferencia:
            if periodo.lower() not in periodos_validos:
                return jsonify({
                    "success": False,
                    "message": f"Período inválido: '{periodo}'. Valores aceitos: {', '.join(periodos_validos)}"
                }), 400
        
        # ===== VALIDAÇÃO: Notificações (opcional) =====
        notificar_campanhas = data.get('notificar_campanhas', True)
        notificar_eventos = data.get('notificar_eventos', True)
        notificar_lembretes = data.get('notificar_lembretes', True)
        
        if not isinstance(notificar_campanhas, bool):
            return jsonify({
                "success": False,
                "message": "notificar_campanhas deve ser true ou false"
            }), 400
        
        # ===== VERIFICAR SE JÁ EXISTE PREFERÊNCIA =====
        preferencia_existente = PreferenciaModel.buscar_por_usuario(current_user['usuario_id'])
        
        if preferencia_existente:
            # ===== ATUALIZAR PREFERÊNCIA EXISTENTE =====
            preferencia = PreferenciaModel.atualizar(
                usuario_id=current_user['usuario_id'],
                dias_preferencia=dias_preferencia,
                periodos_preferencia=periodos_preferencia,
                notificar_campanhas=notificar_campanhas,
                notificar_eventos=notificar_eventos,
                notificar_lembretes=notificar_lembretes,
                tipo_notificacao=data.get('tipo_notificacao', ['email', 'push']),
                hemocentros_favoritos=data.get('hemocentros_favoritos', [])
            )
            
            return jsonify({
                "success": True,
                "message": "Preferências atualizadas com sucesso",
                "preferencias": preferencia
            }), 200
        
        else:
            # ===== CRIAR NOVA PREFERÊNCIA =====
            preferencia = PreferenciaModel.criar(
                usuario_id=current_user['usuario_id'],
                dias_preferencia=dias_preferencia,
                periodos_preferencia=periodos_preferencia,
                notificar_campanhas=notificar_campanhas,
                notificar_eventos=notificar_eventos,
                notificar_lembretes=notificar_lembretes,
                tipo_notificacao=data.get('tipo_notificacao', ['email', 'push']),
                hemocentros_favoritos=data.get('hemocentros_favoritos', [])
            )
            
            return jsonify({
                "success": True,
                "message": "Preferências criadas com sucesso",
                "preferencias": preferencia
            }), 201
        
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        print(f"[ERRO] Salvar preferências: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "Erro interno ao salvar preferências"
        }), 500


# ============== BUSCAR MINHAS PREFERÊNCIAS ==============
@preferencia_bp.route('/minhas_preferencias', methods=['GET'])
@token_required
def buscar_minhas_preferencias(current_user):
    """
    Retorna as preferências de agendamento do usuário autenticado
    Se não existir, retorna preferências padrão
    """
    try:
        preferencia = PreferenciaModel.buscar_por_usuario(current_user['usuario_id'])
        
        if not preferencia:
            # Retornar preferências padrão
            preferencias_padrao = {
                "usuario_id": current_user['usuario_id'],
                "dias_preferencia": ["segunda", "terca", "quarta", "quinta", "sexta"],
                "periodos_preferencia": ["manha", "tarde"],
                "notificar_campanhas": True,
                "notificar_eventos": True,
                "notificar_lembretes": True,
                "tipo_notificacao": ["email", "push"],
                "hemocentros_favoritos": [],
                "data_criacao": None,
                "data_atualizacao": None
            }
            
            return jsonify({
                "success": True,
                "message": "Nenhuma preferência configurada. Retornando padrões.",
                "preferencias": preferencias_padrao,
                "is_default": True
            }), 200
        
        return jsonify({
            "success": True,
            "preferencias": preferencia,
            "is_default": False
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Buscar preferências: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao buscar preferências"
        }), 500


# ============== ATUALIZAR DIAS DE PREFERÊNCIA ==============
@preferencia_bp.route('/minhas_preferencias/dias', methods=['PATCH'])
@token_required
def atualizar_dias_preferencia(current_user):
    """
    Atualiza apenas os dias de preferência do usuário
    """
    try:
        data = request.json
        
        if 'dias_preferencia' not in data:
            return jsonify({
                "success": False,
                "message": "Campo dias_preferencia é obrigatório"
            }), 400
        
        # Validar dias
        dias_validos = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
        dias_preferencia = data['dias_preferencia']
        
        if not isinstance(dias_preferencia, list) or len(dias_preferencia) == 0:
            return jsonify({
                "success": False,
                "message": "dias_preferencia deve ser uma lista com pelo menos um dia"
            }), 400
        
        for dia in dias_preferencia:
            if dia.lower() not in dias_validos:
                return jsonify({
                    "success": False,
                    "message": f"Dia inválido: '{dia}'"
                }), 400
        
        # Atualizar
        PreferenciaModel.atualizar_dias(current_user['usuario_id'], dias_preferencia)
        
        return jsonify({
            "success": True,
            "message": "Dias de preferência atualizados com sucesso"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Atualizar dias: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao atualizar dias de preferência"
        }), 500


# ============== ATUALIZAR PERÍODOS DE PREFERÊNCIA ==============
@preferencia_bp.route('/minhas_preferencias/periodos', methods=['PATCH'])
@token_required
def atualizar_periodos_preferencia(current_user):
    """
    Atualiza apenas os períodos de preferência do usuário
    """
    try:
        data = request.json
        
        if 'periodos_preferencia' not in data:
            return jsonify({
                "success": False,
                "message": "Campo periodos_preferencia é obrigatório"
            }), 400
        
        # Validar períodos
        periodos_validos = ['manha', 'tarde', 'noite']
        periodos_preferencia = data['periodos_preferencia']
        
        if not isinstance(periodos_preferencia, list) or len(periodos_preferencia) == 0:
            return jsonify({
                "success": False,
                "message": "periodos_preferencia deve ser uma lista com pelo menos um período"
            }), 400
        
        for periodo in periodos_preferencia:
            if periodo.lower() not in periodos_validos:
                return jsonify({
                    "success": False,
                    "message": f"Período inválido: '{periodo}'"
                }), 400
        
        # Atualizar
        PreferenciaModel.atualizar_periodos(current_user['usuario_id'], periodos_preferencia)
        
        return jsonify({
            "success": True,
            "message": "Períodos de preferência atualizados com sucesso"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Atualizar períodos: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao atualizar períodos de preferência"
        }), 500


# ============== ATUALIZAR NOTIFICAÇÕES ==============
@preferencia_bp.route('/minhas_preferencias/notificacoes', methods=['PATCH'])
@token_required
def atualizar_notificacoes(current_user):
    """
    Atualiza configurações de notificação do usuário
    """
    try:
        data = request.json
        
        # Campos opcionais
        notificar_campanhas = data.get('notificar_campanhas')
        notificar_eventos = data.get('notificar_eventos')
        notificar_lembretes = data.get('notificar_lembretes')
        tipo_notificacao = data.get('tipo_notificacao')
        
        # Validar tipos de notificação se fornecido
        if tipo_notificacao:
            tipos_validos = ['email', 'sms', 'push', 'whatsapp']
            if not isinstance(tipo_notificacao, list):
                return jsonify({
                    "success": False,
                    "message": "tipo_notificacao deve ser uma lista"
                }), 400
            
            for tipo in tipo_notificacao:
                if tipo not in tipos_validos:
                    return jsonify({
                        "success": False,
                        "message": f"Tipo inválido: '{tipo}'. Valores aceitos: {', '.join(tipos_validos)}"
                    }), 400
        
        # Atualizar
        PreferenciaModel.atualizar_notificacoes(
            usuario_id=current_user['usuario_id'],
            notificar_campanhas=notificar_campanhas,
            notificar_eventos=notificar_eventos,
            notificar_lembretes=notificar_lembretes,
            tipo_notificacao=tipo_notificacao
        )
        
        return jsonify({
            "success": True,
            "message": "Preferências de notificação atualizadas com sucesso"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Atualizar notificações: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao atualizar preferências de notificação"
        }), 500


# ============== ADICIONAR HEMOCENTRO FAVORITO ==============
@preferencia_bp.route('/minhas_preferencias/hemocentros_favoritos/<int:hemocentro_id>', methods=['POST'])
@token_required
def adicionar_hemocentro_favorito(current_uer, hemocentro_id):
    """
    Adiciona um hemocentro aos favoritos do usuário
    """
    try:
        # Verificar se hemocentro existe
        from models import HemocentroModel
        hemocentro = HemocentroModel.buscar_por_id(hemocentro_id)
        
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        
        # Adicionar aos favoritos
        PreferenciaModel.adicionar_hemocentro_favorito(current_uer['usuario_id'], hemocentro_id)
        
        return jsonify({
            "success": True,
            "message": "Hemocentro adicionado aos favoritos"
        }), 200
        
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        print(f"[ERRO] Adicionar favorito: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao adicionar hemocentro aos favoritos"
        }), 500


# ============== REMOVER HEMOCENTRO FAVORITO ==============
@preferencia_bp.route('/minhas_preferencias/hemocentros_favoritos/<int:hemocentro_id>', methods=['DELETE'])
@token_required
def remover_hemocentro_favorito(current_user, hemocentro_id):
    """
    Remove um hemocentro dos favoritos do usuário
    """
    try:
        PreferenciaModel.remover_hemocentro_favorito(current_user['usuario_id'], hemocentro_id)
        
        return jsonify({
            "success": True,
            "message": "Hemocentro removido dos favoritos"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Remover favorito: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao remover hemocentro dos favoritos"
        }), 500


# ============== DELETAR PREFERÊNCIAS ==============
@preferencia_bp.route('/minhas_preferencias', methods=['DELETE'])
@token_required
def deletar_preferencias(current_user):
    """
    Remove todas as preferências do usuário
    Sistema volta a usar configurações padrão
    """
    try:
        PreferenciaModel.deletar(current_user['usuario_id'])
        
        return jsonify({
            "success": True,
            "message": "Preferências deletadas. Configurações padrão serão usadas."
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Deletar preferências: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao deletar preferências"
        }), 500


# ============== BUSCAR HORÁRIOS DISPONÍVEIS BASEADO NAS PREFERÊNCIAS ==============
@preferencia_bp.route('/horarios_sugeridos', methods=['GET'])
@token_required
def buscar_horarios_sugeridos(current_user):
    """
    Retorna horários de agendamento sugeridos baseado nas preferências do usuário
    Query params: id_hemocentro (opcional), data_inicio (opcional)
    """
    try:
        hemocentro_id = request.args.get('hemocentro_id', type=int)
        data_inicio = request.args.get('data_inicio')  # formato: YYYY-MM-DD
        
        # Buscar preferências
        preferencias = PreferenciaModel.buscar_por_usuario(current_user['usuario_id']) or {}
        
        # Buscar horários disponíveis baseado nas preferências
        horarios = PreferenciaModel.buscar_horarios_sugeridos(
            usuario_id=current_user['usuario_id'],
            hemocentro_id=hemocentro_id,
            data_inicio=data_inicio,
            preferencias=preferencias
        )
        
        return jsonify({
            "success": True,
            "total": len(horarios),
            "horarios": horarios
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Buscar horários sugeridos: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao buscar horários sugeridos"
        }), 500