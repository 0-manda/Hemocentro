from flask import Blueprint, request, jsonify
from models.models import AgendamentoModel, HemocentroModel, CampanhaModel, UsuarioModel
from utils.auth_utils import token_required
from datetime import datetime, timezone, timedelta

agendamento_bp = Blueprint('agendamento_bp', __name__)

# ============== CRIAR AGENDAMENTO ==============
@agendamento_bp.route('/cadastrar_agendamento', methods=['POST'])
@token_required
def cadastrar_agendamento(usuario_atual):
    """
    Cria um novo agendamento de doação
    Requer autenticação via token JWT
    """
    try:
        data = request.json
        
        # ===== VALIDAÇÃO: Campos obrigatórios =====
        campos_obrigatorios = ['id_hemocentro', 'data_hora', 'tipo_doacao']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        
        # ===== VALIDAÇÃO: Formato e data futura =====
        try:
            data_agendamento = datetime.fromisoformat(data['data_hora'].replace('Z', '+00:00'))
            if data_agendamento <= datetime.now(timezone.utc):
                return jsonify({
                    "success": False,
                    "message": "A data do agendamento deve ser futura"
                }), 400
            
            # Validar se não é muito distante (ex: máximo 6 meses)
            data_maxima = datetime.now() + timedelta(days=180)
            if data_agendamento > data_maxima:
                return jsonify({
                    "success": False,
                    "message": "Agendamento não pode ser feito com mais de 6 meses de antecedência"
                }), 400
                
        except (ValueError, AttributeError):
            return jsonify({
                "success": False,
                "message": "Formato de data inválido. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
            }), 400
        
        # ===== VALIDAÇÃO: Tipo de doação válido =====
        tipos_validos = ['sangue_total', 'plaquetas', 'plasma', 'aferese']
        if data['tipo_doacao'] not in tipos_validos:
            return jsonify({
                "success": False,
                "message": f"Tipo de doação inválido. Valores aceitos: {', '.join(tipos_validos)}"
            }), 400
        
        # ===== VALIDAÇÃO: Hemocentro existe =====
        hemocentro = HemocentroModel.buscar_por_id(data['id_hemocentro'])
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        
        # ===== VALIDAÇÃO: Campanha existe (se informada) =====
        if data.get('id_campanha'):
            campanha = CampanhaModel.buscar_por_id(data['id_campanha'])
            if not campanha:
                return jsonify({
                    "success": False,
                    "message": "Campanha não encontrada"
                }), 404
        
        # ===== VALIDAÇÃO: Verificar intervalo mínimo entre doações =====
        ultima_doacao = AgendamentoModel.buscar_ultima_doacao(usuario_atual['id_usuario'])
        if ultima_doacao:
            ultima_data = ultima_doacao['data_hora']
            if isinstance(ultima_data, str):
                ultima_data = datetime.fromisoformat(ultima_data.replace('Z', '+00:00'))

            dias_desde_ultima = (data_agendamento - ultima_data).days

            intervalo_minimo = 60 if usuario_atual.get('sexo') == 'M' else 90
            
            if dias_desde_ultima < intervalo_minimo:
                return jsonify({
                    "success": False,
                    "message": f"Intervalo mínimo entre doações não respeitado. Aguarde {intervalo_minimo - dias_desde_ultima} dias"
                }), 400
        
        # ===== CRIAR AGENDAMENTO =====
        agendamento = AgendamentoModel.criar_agendamento(
            id_usuario=usuario_atual['id_usuario'],  # Do token de autenticação
            id_campanha=data.get('id_campanha'),  # Opcional
            id_hemocentro=data['id_hemocentro'],
            data_hora=data['data_hora'],
            status='pendente',  # Padrão do sistema
            tipo_doacao=data['tipo_doacao'],
            observacoes=data.get('observacoes', '')  # Opcional
        )
        
        return jsonify({
            "success": True, 
            "message": "Agendamento criado com sucesso",
            "agendamento": agendamento
        }), 201
        
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        # Log do erro (em produção, usar logging adequado)
        print(f"[ERRO] Criar agendamento: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "Erro interno ao criar agendamento"
        }), 500


# ============== LISTAR AGENDAMENTOS DO USUÁRIO ==============
@agendamento_bp.route('/meus_agendamentos', methods=['GET'])
@token_required
def listar_meus_agendamentos(usuario_atual):
    """
    Lista todos os agendamentos do usuário autenticado
    Query params opcionais: status (pendente, confirmado, cancelado, realizado)
    """
    try:
        status = request.args.get('status')  # Filtro opcional
        
        agendamentos = AgendamentoModel.listar_por_usuario(
            id_usuario=usuario_atual['id_usuario'],
            status=status
        )
        
        return jsonify({
            "success": True,
            "total": len(agendamentos),
            "agendamentos": agendamentos
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Listar agendamentos: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao buscar agendamentos"
        }), 500


# ============== BUSCAR AGENDAMENTO ESPECÍFICO ==============
@agendamento_bp.route('/agendamento/<int:id_agendamento>', methods=['GET'])
@token_required
def buscar_agendamento(usuario_atual, id_agendamento):
    """
    Busca detalhes de um agendamento específico
    Usuário só pode ver seus próprios agendamentos
    """
    try:
        agendamento = AgendamentoModel.buscar_por_id(id_agendamento)
        
        if not agendamento:
            return jsonify({
                "success": False,
                "message": "Agendamento não encontrado"
            }), 404
        
        # Verificar se o agendamento pertence ao usuário
        if agendamento['id_usuario'] != usuario_atual['id_usuario']:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para acessar este agendamento"
            }), 403
        
        return jsonify({
            "success": True,
            "agendamento": agendamento
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Buscar agendamento: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao buscar agendamento"
        }), 500


# ============== ATUALIZAR AGENDAMENTO ==============
@agendamento_bp.route('/agendamento/<int:id_agendamento>', methods=['PUT'])
@token_required
def atualizar_agendamento(usuario_atual, id_agendamento):
    """
    Atualiza um agendamento existente
    Apenas agendamentos 'pendente' ou 'confirmado' podem ser alterados
    """
    try:
        agendamento = AgendamentoModel.buscar_por_id(id_agendamento)
        
        if not agendamento:
            return jsonify({
                "success": False,
                "message": "Agendamento não encontrado"
            }), 404
        
        # Verificar permissão
        if agendamento['id_usuario'] != usuario_atual['id_usuario']:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para alterar este agendamento"
            }), 403
        
        # Verificar se pode ser alterado
        if agendamento['status'] not in ['pendente', 'confirmado']:
            return jsonify({
                "success": False,
                "message": f"Agendamentos com status '{agendamento['status']}' não podem ser alterados"
            }), 400
        
        data = request.json
        campos_editaveis = ['data_hora', 'tipo_doacao', 'observacoes']
        dados_atualizacao = {}
        
        # Validar data se estiver sendo alterada
        if 'data_hora' in data:
            try:
                nova_data = datetime.fromisoformat(data['data_hora'].replace('Z', '+00:00'))
                if nova_data <= datetime.now(timezone.utc):
                    return jsonify({
                        "success": False,
                        "message": "A nova data deve ser futura"
                    }), 400
                dados_atualizacao['data_hora'] = data['data_hora']
            except (ValueError, AttributeError):
                return jsonify({
                    "success": False,
                    "message": "Formato de data inválido"
                }), 400
        
        # Validar tipo de doação se estiver sendo alterado
        if 'tipo_doacao' in data:
            tipos_validos = ['sangue_total', 'plaquetas', 'plasma', 'aferese']
            if data['tipo_doacao'] not in tipos_validos:
                return jsonify({
                    "success": False,
                    "message": "Tipo de doação inválido"
                }), 400
            dados_atualizacao['tipo_doacao'] = data['tipo_doacao']
        
        if 'observacoes' in data:
            dados_atualizacao['observacoes'] = data['observacoes']
        
        if not dados_atualizacao:
            return jsonify({
                "success": False,
                "message": "Nenhum campo válido para atualizar"
            }), 400
        
        # Atualizar agendamento
        agendamento_atualizado = AgendamentoModel.atualizar_agendamento(id_agendamento, dados_atualizacao)
        
        return jsonify({
            "success": True,
            "message": "Agendamento atualizado com sucesso",
            "agendamento": agendamento_atualizado
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Atualizar agendamento: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao atualizar agendamento"
        }), 500


# ============== CANCELAR AGENDAMENTO ==============
@agendamento_bp.route('/agendamento/<int:id_agendamento>', methods=['DELETE'])
@token_required
def cancelar_agendamento(usuario_atual, id_agendamento):
    """
    Cancela um agendamento
    Apenas agendamentos 'pendente' ou 'confirmado' podem ser cancelados
    """
    try:
        agendamento = AgendamentoModel.buscar_por_id(id_agendamento)
        
        if not agendamento:
            return jsonify({
                "success": False,
                "message": "Agendamento não encontrado"
            }), 404
        
        # Verificar permissão
        if agendamento['id_usuario'] != usuario_atual['id_usuario']:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para cancelar este agendamento"
            }), 403
        
        # Verificar se pode ser cancelado
        if agendamento['status'] not in ['pendente', 'confirmado']:
            return jsonify({
                "success": False,
                "message": f"Agendamentos com status '{agendamento['status']}' não podem ser cancelados"
            }), 400
        
        # Cancelar agendamento
        AgendamentoModel.cancelar_agendamento(id_agendamento)
        
        return jsonify({
            "success": True,
            "message": "Agendamento cancelado com sucesso"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Cancelar agendamento: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao cancelar agendamento"
        }), 500