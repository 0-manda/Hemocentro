from flask import Blueprint, request, jsonify
from models.models import ContatoModel, HemocentroModel, UsuarioModel
from utils.auth_utils import hemocentro_required, token_required, validar_email, only_numbers
from datetime import datetime


contato_bp = Blueprint('contato_bp', __name__)

@contato_bp.route('/contato', methods=['POST'])
def enviar_contato():
    try:
        data = request.json or {}
        campos_necessarios = ['nome', 'email', 'mensagem', 'hemocentro_id']
        for campo in campos_necessarios:
            if campo not in data or not data.get(campo):
                return jsonify({"success": False, "message": f"Campo obrigatório faltando: {campo}" }), 400
            
        nome=data['nome'].strip()
        email=data['email'].strip().lower()
        mensagem=data['mensagem'].strip()
        hemocentro_id=data['hemocentro_id']

        if len(nome) < 3:
            return jsonify({"success": False, "message": "Nome deve ter pelo menos 3 caracteres."}), 400
        if len(nome) > 100:
            return jsonify({"success": False, "message": "Nome deve ter no máximo 100 caracteres."}), 400
        if not validar_email(email):
            return jsonify({"success": False, "message": "Email inválido."}), 400
        if len(mensagem) < 10:
            return jsonify({"success": False, "message": "Mensagem deve ter pelo menos 10 caracteres."}), 400
        if len(mensagem) > 1000:
            return jsonify({"success": False, "message": "Mensagem deve ter no máximo 1000 caracteres."}), 400
        if hemocentro_id:
            hemocentro = HemocentroModel.buscar_por_id(hemocentro_id)
            if not hemocentro:
                return jsonify({"success": False, "message": "Hemocentro não encontrado."}), 404
        if not hemocentro.get('ativo', False):
            return jsonify({"success": False, "message": "Hemocentro inativo."}), 400
        contato = ContatoModel.criar_contato(
            nome=nome,
            email=email,
            mensagem=mensagem,
            hemocentro_id=hemocentro_id,
            data_envio=datetime.now()
            )
        return jsonify({"success": True, "message": "Contato enviado com sucesso."}), 201
    except ValueError as e:
        return jsonify({"success": False, "Erro de validação.": str(e)}), 400
    except Exception as e:
        print("Erro ao enviar contato:", str(e))
        return jsonify({"success": False, "message": "Erro ao enviar contato."}), 500

@contato_bp.route('/contatos', methods=['GET'])
@token_required
@hemocentro_required
def listar_contatos(current_user):
    try:
        # Busca hemocentro do usuário logado
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado."
            }), 404
        
        
        # Lista contatos
        contatos = ContatoModel.listar_por_hemocentro(
            hemocentro_id=hemocentro['hemocentro_id'],
        )
        
        # Conta não lidas
        
        return jsonify({
            "success": True,
            "contatos": contatos,
            "total": len(contatos),
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar contatos: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== BUSCAR CONTATO POR ID (HEMOCENTRO) =====

@contato_bp.route('/contatos/<int:contato_id>', methods=['GET'])
@token_required
@hemocentro_required
def buscar_contato(current_user, contato_id):
    """
    NOVO: Busca detalhes de uma mensagem específica
    MOTIVO: Ver detalhes completos + marcar como lida
    
    SEGURANÇA: Só pode ver mensagens do próprio hemocentro
    """
    try:
        # Busca contato
        contato = ContatoModel.buscar_por_id(contato_id)
        
        if not contato:
            return jsonify({
                "success": False,
                "message": "Mensagem não encontrada."
            }), 404
        
        # SEGURANÇA: Verifica se pertence ao hemocentro do usuário
        
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        
        if contato['hemocentro_id'] != hemocentro['hemocentro_id']:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para ver esta mensagem."
            }), 403
        
        # Marca como lida automaticamente
        if not contato.get('lida', False):
            ContatoModel.marcar_como_lida(contato_id)
            contato['lida'] = True
        
        return jsonify({
            "success": True,
            "contato": contato
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar contato: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500

# ===== DELETAR CONTATO (HEMOCENTRO) =====

@contato_bp.route('/contatos/<int:contato_id>', methods=['DELETE'])
@token_required
@hemocentro_required
def deletar_contato(current_user, contato_id):
    """
    NOVO: Deleta mensagem
    MOTIVO: Gerenciamento de caixa de entrada
    
    SEGURANÇA: Só pode deletar mensagens do próprio hemocentro
    """
    try:
        # Busca contato
        contato = ContatoModel.buscar_por_id(contato_id)
        
        if not contato:
            return jsonify({
                "success": False,
                "message": "Mensagem não encontrada."
            }), 404
        
        # SEGURANÇA: Verifica permissão
        
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        
        if contato['hemocentro_id'] != hemocentro['hemocentro_id']:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão."
            }), 403
        
        # Deleta (ou soft delete, dependendo da sua preferência)
        ContatoModel.deletar(contato_id)
        
        return jsonify({
            "success": True,
            "message": "Mensagem deletada com sucesso."
        }), 200
        
    except Exception as e:
        print(f"Erro ao deletar contato: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== ESTATÍSTICAS DE CONTATO (HEMOCENTRO) =====

@contato_bp.route('/contatos/estatisticas', methods=['GET'])
@token_required
@hemocentro_required
def estatisticas_contatos(current_user):
    """
    NOVO: Estatísticas de mensagens recebidas
    MOTIVO: Dashboard do hemocentro
    """
    try:
        # Busca hemocentro
        
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado."
            }), 404
        
        # Busca estatísticas
        stats = ContatoModel.obter_estatisticas(hemocentro['hemocentro_id'])
        
        return jsonify({
            "success": True,
            "estatisticas": stats
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500