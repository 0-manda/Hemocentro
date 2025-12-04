# from flask import Blueprint, request, jsonify, g
# from models import ContatoModel, HemocentroModel
# from utils.auth_utils import requer_colaborador, validar_email
# from datetime import datetime

# contato_bp = Blueprint('contato_bp', __name__)

# Helper: Buscar hemocentro do sistema

# Enviar contato (público)
# @contato_bp.route('/contato', methods=['POST'])
# def enviar_contato():
#     """
#     Envia mensagem de contato para o hemocentro
#     Rota PÚBLICA - qualquer pessoa pode enviar
    
#     IMPORTANTE: Em produção, adicionar rate limiting (ex: 5 mensagens por hora por IP)
#     """
#     try:
#         data = request.json or {}
        
# Validação: Campos obrigatórios
#         campos_obrigatorios = ['nome', 'email', 'mensagem']
#         for campo in campos_obrigatorios:
#             if not data.get(campo):
#                 return jsonify({
#                     "success": False, 
#                     "message": f"Campo obrigatório faltando: {campo}"
#                 }), 400
        
# Extrair e limpar dados
#         nome = data['nome'].strip()
#         email = data['email'].strip().lower()
#         mensagem = data['mensagem'].strip()
        
# Validação: Nome
#         if len(nome) < 3:
#             return jsonify({
#                 "success": False, 
#                 "message": "Nome deve ter pelo menos 3 caracteres"
#             }), 400
        
#         if len(nome) > 100:
#             return jsonify({
#                 "success": False, 
#                 "message": "Nome muito longo (máximo 100 caracteres)"
#             }), 400
        
# Validação: Email
#         if not validar_email(email):
#             return jsonify({
#                 "success": False, 
#                 "message": "Email inválido"
#             }), 400
        
# Validação: Mensagem
#         if len(mensagem) < 10:
#             return jsonify({
#                 "success": False, 
#                 "message": "Mensagem muito curta (mínimo 10 caracteres)"
#             }), 400
        
#         if len(mensagem) > 2000:
#             return jsonify({
#                 "success": False, 
#                 "message": "Mensagem muito longa (máximo 2000 caracteres)"
#             }), 400
        
# Buscar hemocentro
#         # Para MVP: Sempre envia para o único hemocentro do sistema
#         hemocentro = obter_hemocentro_sistema()
        
#         if not hemocentro:
#             return jsonify({
#                 "success": False, 
#                 "message": "Serviço temporariamente indisponível. Tente novamente mais tarde."
#             }), 503
        
#         if not hemocentro.get('ativo', False):
#             return jsonify({
#                 "success": False, 
#                 "message": "Hemocentro temporariamente desativado"
#             }), 503
        
# Criar contato
#         contato = ContatoModel.criar(
#             id_hemocentro=hemocentro['id_hemocentro'],
#             nome=nome,
#             email=email,
#             mensagem=mensagem
#         )
        
#         return jsonify({
#             "success": True, 
#             "message": "Mensagem enviada com sucesso! Responderemos em breve.",
#             "contato_id": contato['id_contato']
#         }), 201
        
#     except ValueError as ve:
#         return jsonify({
#             "success": False, 
#             "message": str(ve)
#         }), 400
#     except Exception as e:
#         print(f"[ERRO] Enviar contato: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False, 
#             "message": "Erro ao enviar mensagem. Tente novamente."
#         }), 500


# Listar contatos (colaborador)
# @contato_bp.route('/contatos', methods=['GET'])
# @requer_colaborador  # Remove @token_required duplicado
# def listar_contatos(current_user):
#     """
#     Lista todas as mensagens de contato do hemocentro
#     Rota PROTEGIDA - apenas COLABORADORES podem ver
    
#     Query params opcionais:
#       - respondido: true/false (filtrar por respondidas/não respondidas)
#       - limite: número de mensagens (default: todas)
#     """
#     try:
#         # Filtros opcionais
#         apenas_nao_respondidas = request.args.get('respondido', '').lower() == 'false'
#         limite = request.args.get('limite', type=int)
        
#         # Usa g.id_hemocentro diretamente (já disponível!)
#         contatos = ContatoModel.listar_por_hemocentro(
#             id_hemocentro=g.id_hemocentro,
#             apenas_nao_respondidas=apenas_nao_respondidas,
#             limite=limite
#         )
        
#         # Contar não respondidas
#         total_nao_respondidas = sum(1 for c in contatos if not c.get('respondido', False))
        
#         return jsonify({
#             "success": True,
#             "contatos": contatos,
#             "total": len(contatos),
#             "nao_respondidas": total_nao_respondidas
#         }), 200
        
#     except Exception as e:
#         print(f"[ERRO] Listar contatos: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False,
#             "message": "Erro ao listar mensagens"
#         }), 500


# Buscar contato por id (colaborador)
# @contato_bp.route('/contatos/<int:contato_id>', methods=['GET'])
# @requer_colaborador  # Remove @token_required duplicado
# def buscar_contato(current_user, contato_id):
#     """
#     Busca detalhes de uma mensagem específica
#     Rota PROTEGIDA - apenas COLABORADORES
    
#     NÃO marca automaticamente como respondido (apenas ao responder de fato)
#     """
#     try:
#         # Buscar contato
#         contato = ContatoModel.buscar_por_id(contato_id)
        
#         if not contato:
#             return jsonify({
#                 "success": False,
#                 "message": "Mensagem não encontrada"
#             }), 404
        
#         # Verificar se pertence ao hemocentro do colaborador
#         if contato['id_hemocentro'] != g.id_hemocentro:
#             return jsonify({
#                 "success": False,
#                 "message": "Você não tem permissão para ver esta mensagem"
#             }), 403
        
#         return jsonify({
#             "success": True,
#             "contato": contato
#         }), 200
        
#     except Exception as e:
#         print(f"[ERRO] Buscar contato: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False,
#             "message": "Erro ao buscar mensagem"
#         }), 500


# Marcar como respondido (colaborador)
# @contato_bp.route('/contatos/<int:contato_id>/respondido', methods=['PATCH'])
# @requer_colaborador  # Remove @token_required duplicado
# def marcar_respondido(current_user, contato_id):
#     """
#     Marca mensagem como respondida
#     Rota PROTEGIDA - apenas COLABORADORES
#     """
#     try:
#         contato = ContatoModel.buscar_por_id(contato_id)
        
#         if not contato:
#             return jsonify({
#                 "success": False,
#                 "message": "Mensagem não encontrada"
#             }), 404
        
#         # SEGURANÇA: Verificar permissão usando g.id_hemocentro
#         if contato['id_hemocentro'] != g.id_hemocentro:
#             return jsonify({
#                 "success": False,
#                 "message": "Você não tem permissão"
#             }), 403
        
#         # Marcar como respondido
#         sucesso = ContatoModel.marcar_como_respondido(contato_id)
        
#         if not sucesso:
#             return jsonify({
#                 "success": False,
#                 "message": "Erro ao marcar como respondido"
#             }), 500
        
#         return jsonify({
#             "success": True,
#             "message": "Mensagem marcada como respondida"
#         }), 200
        
#     except Exception as e:
#         print(f"[ERRO] Marcar como respondido: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False,
#             "message": "Erro ao atualizar mensagem"
#         }), 500


# Marcar como não respondido (colaborador)
# @contato_bp.route('/contatos/<int:contato_id>/nao-respondido', methods=['PATCH'])
# @requer_colaborador  # Remove @token_required duplicado
# def marcar_nao_respondido(current_user, contato_id):
#     """
#     Marca mensagem como não respondida
#     Rota PROTEGIDA - apenas COLABORADORES
#     Útil para marcar mensagens que precisam ser revisitadas
#     """
#     try:
#         contato = ContatoModel.buscar_por_id(contato_id)
        
#         if not contato:
#             return jsonify({
#                 "success": False,
#                 "message": "Mensagem não encontrada"
#             }), 404
        
#         # SEGURANÇA: Verificar permissão usando g.id_hemocentro
#         if contato['id_hemocentro'] != g.id_hemocentro:
#             return jsonify({
#                 "success": False,
#                 "message": "Você não tem permissão"
#             }), 403
        
#         # Marcar como não respondido
#         sucesso = ContatoModel.marcar_como_nao_respondido(contato_id)
        
#         if not sucesso:
#             return jsonify({
#                 "success": False,
#                 "message": "Erro ao atualizar mensagem"
#             }), 500
        
#         return jsonify({
#             "success": True,
#             "message": "Mensagem marcada como não respondida"
#         }), 200
        
#     except Exception as e:
#         print(f"[ERRO] Marcar como não respondido: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False,
#             "message": "Erro ao atualizar mensagem"
#         }), 500


# Deletar contato (colaborador)
# @contato_bp.route('/contatos/<int:contato_id>', methods=['DELETE'])
# @requer_colaborador  # Remove @token_required duplicado
# def deletar_contato(current_user, contato_id):
#     """
#     Deleta uma mensagem de contato
#     Rota PROTEGIDA - apenas COLABORADORES
#     """
#     try:
#         contato = ContatoModel.buscar_por_id(contato_id)
        
#         if not contato:
#             return jsonify({
#                 "success": False,
#                 "message": "Mensagem não encontrada"
#             }), 404
        
#         # SEGURANÇA: Verificar permissão usando g.id_hemocentro
#         if contato['id_hemocentro'] != g.id_hemocentro:
#             return jsonify({
#                 "success": False,
#                 "message": "Você não tem permissão"
#             }), 403
        
#         # Deletar
#         sucesso = ContatoModel.deletar(contato_id)
        
#         if not sucesso:
#             return jsonify({
#                 "success": False,
#                 "message": "Erro ao deletar mensagem"
#             }), 500
        
#         return jsonify({
#             "success": True,
#             "message": "Mensagem deletada com sucesso"
#         }), 200
        
#     except Exception as e:
#         print(f"[ERRO] Deletar contato: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False,
#             "message": "Erro ao deletar mensagem"
#         }), 500


# Contar não respondidas (colaborador)
# @contato_bp.route('/contatos/nao-respondidas/count', methods=['GET'])
# @requer_colaborador  # Remove @token_required duplicado
# def contar_nao_respondidas(current_user):
#     """
#     Retorna quantidade de mensagens não respondidas
#     Rota PROTEGIDA - apenas COLABORADORES
#     Útil para badge de notificações no dashboard
#     """
#     try:
	# Usa g.id_hemocentro diretamente
	#total = ContatoModel.contar_nao_respondidas(g.id_hemocentro)
        
#         return jsonify({
#             "success": True,
#             "nao_respondidas": total
#         }), 200
        
#     except Exception as e:
#         print(f"[ERRO] Contar não respondidas: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False,
#             "message": "Erro ao contar mensagens"
#         }), 500