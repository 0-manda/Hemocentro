from flask import Blueprint, request, jsonify, g
from back.utils.auth_utils import requer_doador
from back.models import PreferenciaModel

preferencia_bp = Blueprint('preferencia_bp', __name__)

# criar/atualizar preferências
@preferencia_bp.route('/minhas_preferencias', methods=['POST', 'PUT'])
@requer_doador
def salvar_preferencias(current_user):
    try:
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "message": "Corpo da requisição não pode estar vazio"
            }), 400
        if 'dias_preferencia' not in data:
            return jsonify({
                "success": False,
                "message": "Campo obrigatório: dias_preferencia"
            }), 400
        if 'periodos_preferencia' not in data:
            return jsonify({
                "success": False,
                "message": "Campo obrigatório: periodos_preferencia"
            }), 400
        dias_validos = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
        dias_preferencia = data['dias_preferencia']
        if not isinstance(dias_preferencia, list):
            return jsonify({
                "success": False,
                "message": "dias_preferencia deve ser uma lista"
            }), 400
        if len(dias_preferencia) == 0:
            return jsonify({
                "success": False,
                "message": "Selecione pelo menos um dia da semana"
            }), 400
        for dia in dias_preferencia:
            if not isinstance(dia, str):
                return jsonify({
                    "success": False,
                    "message": "Todos os dias devem ser strings"
                }), 400
            if dia.lower() not in dias_validos:
                return jsonify({
                    "success": False,
                    "message": f"Dia inválido: '{dia}'. Valores aceitos: {', '.join(dias_validos)}"
                }), 400
        periodos_validos = ['manha', 'tarde', 'noite']
        periodos_preferencia = data['periodos_preferencia']
        if not isinstance(periodos_preferencia, list):
            return jsonify({
                "success": False,
                "message": "periodos_preferencia deve ser uma lista"
            }), 400
        if len(periodos_preferencia) == 0:
            return jsonify({
                "success": False,
                "message": "Selecione pelo menos um período do dia"
            }), 400
        for periodo in periodos_preferencia:
            if not isinstance(periodo, str):
                return jsonify({
                    "success": False,
                    "message": "Todos os períodos devem ser strings"
                }), 400
            if periodo.lower() not in periodos_validos:
                return jsonify({
                    "success": False,
                    "message": f"Período inválido: '{periodo}'. Valores aceitos: {', '.join(periodos_validos)}"
                }), 400
        dias_preferencia = [dia.lower() for dia in dias_preferencia]
        periodos_preferencia = [periodo.lower() for periodo in periodos_preferencia]
        # ve se já tem preferência e atualiza ou cria
        preferencia_existente = PreferenciaModel.buscar_por_usuario(g.id_usuario)
        if preferencia_existente:
            preferencia = PreferenciaModel.atualizar(
                id_usuario=g.id_usuario,
                dias_preferencia=dias_preferencia,
                periodos_preferencia=periodos_preferencia
            )
            return jsonify({
                "success": True,
                "message": "Preferências atualizadas com sucesso",
                "data": preferencia
            }), 200
        else:
            preferencia = PreferenciaModel.criar(
                id_usuario=g.id_usuario,
                dias_preferencia=dias_preferencia,
                periodos_preferencia=periodos_preferencia
            )
            return jsonify({
                "success": True,
                "message": "Preferências criadas com sucesso",
                "data": preferencia
            }), 201     
    except ValueError as ve:
        return jsonify({
            "success": False,
            "message": str(ve)
        }), 400
    except Exception as e:
        print(f"[ERRO] Salvar preferências: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro interno ao salvar preferências"
        }), 500

# buscar preferências (reotrna padrão se não tiver)
@preferencia_bp.route('/minhas_preferencias', methods=['GET'])
@requer_doador
def buscar_minhas_preferencias(current_user):
    try:
        preferencia = PreferenciaModel.buscar_por_usuario(g.id_usuario)
        if not preferencia:
            preferencias_padrao = {
                "id_usuario": g.id_usuario,
                "dias_preferencia": ["segunda", "terca", "quarta", "quinta", "sexta"],
                "periodos_preferencia": ["manha", "tarde"],
                "data_atualizacao": None,
                "is_default": True
            }
            return jsonify({
                "success": True,
                "message": "Nenhuma preferência configurada. Retornando valores padrão.",
                "data": preferencias_padrao
            }), 200
        preferencia['is_default'] = False
        return jsonify({
            "success": True,
            "data": preferencia
        }), 200
    except Exception as e:
        print(f"[ERRO] Buscar preferências: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao buscar preferências"
        }), 500

# deleta
@preferencia_bp.route('/minhas_preferencias', methods=['DELETE'])
@requer_doador
def deletar_preferencias(current_user):
    try:
        preferencia = PreferenciaModel.buscar_por_usuario(g.id_usuario)
        if not preferencia:
            return jsonify({
                "success": False,
                "message": "Você não possui preferências cadastradas"
            }), 404
        PreferenciaModel.deletar(g.id_usuario)
        return jsonify({
            "success": True,
            "message": "Preferências deletadas com sucesso. Valores padrão serão usados."
        }), 200  
    except Exception as e:
        print(f"[ERRO] Deletar preferências: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao deletar preferências"
        }), 500