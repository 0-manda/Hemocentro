from flask import Blueprint, request, jsonify
from utils.auth_utils import hemocentro_required, token_required, only_numbers
from models.models import HistoricoModel, AgendamentoModel, UsuarioModel, HemocentroModel
from datetime import datetime, timedelta

historico_bp = Blueprint('historico_bp', __name__)

@historico_bp.route('/cadastrar_historico', methods=['POST'])
@hemocentro_required
def registrar_doacao(current_user):
    try:
        data = request.json or {}
        campos_necessarios = ['agendamento_id', 'quantidade_ml', 'tipo_doacao', 'observacoes']
        for campo in campos_necessarios:    
            if campo not in data or not data.get(campo):
                return jsonify({"success": False, "message": f"Campo obrigatório faltando: {campo}" }), 400
        
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)

        if not hemocentro:
            return jsonify({"success": False, "message": "Hemocentro não encontrado para o usuário autenticado."}), 404
        hemo = hemocentro['hemocentro_id']
        agendamento_id = data['agendamento_id']
        agendamento = AgendamentoModel.buscar_por_id(agendamento_id)

        if not agendamento:
            return jsonify({"success": False, "message": "Agendamento não encontrado."}), 404
        if agendamento['hemocentro_id'] != hemo:
            return jsonify({"success": False, "message": "Agendamento não pertence ao hemocentro autenticado."}),404
        if agendamento['status'] not in ['confirmado', 'pendente']:
            return jsonify({"success": False, "message": "Agendamento não está em um estado válido para registrar doação."}),404
        if HistoricoModel.buscar_por_agendamento(data['agendamento_id']):
            return jsonify({"success": False, "message": "Doação já registrada para este agendamento."}),404
        try:
            quantidade_ml = int(data['quantidade_ml'])
            if quantidade_ml <200 or quantidade_ml > 600:
                return jsonify({"success": False, "message": "Quantidade de doação deve ser entre 200ml e 600ml."}), 400
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "Quantidade de doação inválida."}), 400
        tipos_validos = ['sangue', 'plaquetas', 'plasma', 'medula_ossea']
        tipo_doacao = data['tipo_doacao'].lower()
        
        if tipo_doacao not in tipos_validos:
            return jsonify({"success": False, "message": "Tipo de doação inválido."}), 400
        
        doador = UsuarioModel.buscar_por_id(agendamento['usuario_id'])
        dias_intervalo = 60
        data_doacao = datetime.now()
        proxima_doacao_permitida = data_doacao + timedelta(days=dias_intervalo)
        historico = HistoricoModel.registrar_doacao(
            usuario_id=agendamento['usuario_id'],
            hemocentro_id=hemo,
            agendamento_id=agendamento_id,
            data_doacao=data_doacao,
            quantidade_ml=quantidade_ml,
            tipo_doacao=tipo_doacao,
            observacoes=data.get('observacoes', '').strip(),
            proxima_doacao_permitida=proxima_doacao_permitida,
            data_registro=datetime.now()
        )
        AgendamentoModel.atualizar_status(agendamento_id, 'concluído')
        return jsonify ({"success":True, "message": "Doação registrada com sucesso!",
            "historico_id": historico,
            "proxima_doacao_permitida": proxima_doacao_permitida.strftime('%Y-%m-%d')
        }), 201
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": f"Erro de validação: {str(e)}"
        }), 400
    except Exception as e:
        print(f"Erro ao registrar doação: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== LISTAR HISTÓRICO DO USUÁRIO =====

@historico_bp.route('/minhas-doacoes', methods=['GET'])
@token_required
def minhas_doacoes(current_user):
    """
    NOVO: Lista histórico de doações do usuário logado
    MOTIVO: Doador precisa ver seu próprio histórico
    """
    try:
        usuario_id = current_user['usuario_id']
        
        historico = HistoricoModel.listar_por_usuario(usuario_id)
        
        # Calcula estatísticas
        total_doacoes = len(historico)
        total_ml = sum(d['quantidade_ml'] for d in historico)
        
        # Próxima doação permitida (da doação mais recente)
        proxima_doacao = None
        if historico:
            proxima_doacao = historico[0].get('proxima_doacao_permitida') if historico else None
        
        return jsonify({
            "success": True,
            "doacoes": historico,
            "estatisticas": {
                "total_doacoes": total_doacoes,
                "total_ml": total_ml,
                "proxima_doacao_permitida": str(proxima_doacao) if proxima_doacao else None
            }
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar histórico: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== LISTAR DOAÇÕES DO HEMOCENTRO =====

@historico_bp.route('/doacoes', methods=['GET'])
@token_required
@hemocentro_required
def listar_doacoes_hemocentro(current_user):
    """
    NOVO: Lista todas as doações recebidas pelo hemocentro
    MOTIVO: Dashboard do hemocentro
    
    Filtros opcionais:
      - ?data_inicio=2025-01-01
      - ?data_fim=2025-12-31
      - ?tipo_doacao=sangue_total
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
        
        # Filtros
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        tipo_doacao = request.args.get('tipo_doacao')
        
        doacoes = HistoricoModel.listar_por_hemocentro(
            hemocentro_id=hemocentro['hemocentro_id'],
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo_doacao=tipo_doacao
        )
        
        # Estatísticas
        total_doacoes = len(doacoes)
        total_ml = sum(d['quantidade_ml'] for d in doacoes)
        
        return jsonify({
            "success": True,
            "doacoes": doacoes,
            "total": total_doacoes,
            "total_ml": total_ml
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar doações: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== BUSCAR DOAÇÃO POR ID =====

@historico_bp.route('/doacoes/<int:historico_id>', methods=['GET'])
@token_required
def buscar_doacao(current_user, historico_id):
    """
    NOVO: Busca detalhes de uma doação específica
    MOTIVO: Ver detalhes completos
    
    SEGURANÇA: Usuário só vê suas próprias doações OU hemocentro vê doações recebidas
    """
    try:
        doacao = HistoricoModel.buscar_por_id(historico_id)
        
        if not doacao:
            return jsonify({
                "success": False,
                "message": "Doação não encontrada."
            }), 404
        
        # SEGURANÇA: Verifica permissão
        usuario_id = current_user['usuario_id']
        tipo_usuario = current_user['tipo_usuario']
        
        if tipo_usuario == 'doador':
            # Doador só vê suas próprias doações
            if doacao['usuario_id'] != usuario_id:
                return jsonify({
                    "success": False,
                    "message": "Você não tem permissão para ver esta doação."
                }), 403
        
        elif tipo_usuario == 'hemocentro':
            # Hemocentro só vê doações recebidas por ele
            usuario = UsuarioModel.buscar_por_id(usuario_id)
            cnpj = only_numbers(usuario['cpf_cnpj'])
            hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
            
            if doacao['hemocentro_id'] != hemocentro['hemocentro_id']:
                return jsonify({
                    "success": False,
                    "message": "Esta doação não foi realizada no seu hemocentro."
                }), 403
        
        return jsonify({
            "success": True,
            "doacao": doacao
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar doação: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500