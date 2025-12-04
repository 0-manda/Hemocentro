# from flask import Blueprint, request, jsonify
# from back.utils.auth_utils import hemocentro_required
# from back.models import NotificacaoModel

# notificacao_bp = Blueprint('notificacao_bp', __name__)

# @notificacao_bp.route('/cadastrar_notificacao', methods=['POST'])
# @hemocentro_required
# def cadastrar_notificacao():
#     try:
#         data = request.json
#         campos_necessarios = ['id_usuario', 'id_campanha', 'tipo', 'assunto', 'mensagem', 'enviado', 'data_agendamento', 'data_envio']
#         for campo in campos_necessarios:
#             if not data.get (campo):
#                 return jsonify({"success": False, "message": f"Campo obrigatório faltando: {campo}" }), 400
        
#         notificacao = NotificacaoModel.criar(
#             id_usuario=data['id_usuario'],
#             id_campanha=data['id_campanha'],
#             tipo=data['tipo'],
#             assunto=data['assunto'],
#             mensagem=data['mensagem'],
#             enviado=data['enviado'],
#             data_agendamento=data['data_agendamento'],
#             data_envio=data['data_envio']
#         )
#         return jsonify({"success": True, "user": notificacao}), 201
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 400