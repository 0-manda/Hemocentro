from flask import Blueprint, request, jsonify, g
from back.utils.auth_utils import requer_colaborador, requer_doador, token_required
from back.models import HistoricoModel, AgendamentoModel, CampanhaModel
from datetime import datetime, timedelta

historico_bp = Blueprint('historico_bp', __name__)

# calculo de próxima doação
def calcular_proxima_doacao(tipo_doacao):
    agora = datetime.now()
    if tipo_doacao == 'sangue_total':
        #intervalo médio 75 dias (entre 60-90)
        return agora + timedelta(days=75)
    elif tipo_doacao in ['plaquetas', 'plasma']:
        #intervalo 48 horas
        return agora + timedelta(days=2)
    elif tipo_doacao == 'aferese':
        #intervalo 1 semana
        return agora + timedelta(days=7)
    else:
        #padrão 60 dias
        return agora + timedelta(days=60)

# registrar doação
@historico_bp.route('/doacoes/registrar', methods=['POST'])
@requer_colaborador
def registrar_doacao(current_user):
    try:
        data = request.json or {}
        campos_obrigatorios = ['id_agendamento', 'quantidade_ml', 'tipo_doacao']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False,
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        id_agendamento = data['id_agendamento']
        observacoes = data.get('observacoes', '').strip() if data.get('observacoes') else None

        agendamento = AgendamentoModel.buscar_por_id(id_agendamento)
        if not agendamento:
            return jsonify({
                "success": False,
                "message": "Agendamento não encontrado"
            }), 404
        if agendamento.get('id_hemocentro') != g.id_hemocentro:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para registrar esta doação"
            }), 403

        status_validos = ['pendente', 'confirmado']
        if agendamento.get('status') not in status_validos:
            return jsonify({
                "success": False,
                "message": f"Agendamento não pode ser registrado. Status atual: {agendamento.get('status')}"
            }), 400
        
        if HistoricoModel.buscar_por_agendamento(id_agendamento):
            return jsonify({
                "success": False,
                "message": "Doação já foi registrada para este agendamento"
            }), 409

        try:
            quantidade_ml = int(data['quantidade_ml'])
            if quantidade_ml < 200 or quantidade_ml > 600:
                return jsonify({
                    "success": False,
                    "message": "Quantidade deve estar entre 200ml e 600ml"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Quantidade deve ser um número inteiro"
            }), 400

        tipos_validos = ['sangue_total', 'plaquetas', 'plasma', 'aferese']
        tipo_doacao = data['tipo_doacao'].lower()
        
        if tipo_doacao not in tipos_validos:
            return jsonify({
                "success": False,
                "message": f"Tipo de doação inválido. Use: {', '.join(tipos_validos)}"
            }), 400

        proxima_doacao = calcular_proxima_doacao(tipo_doacao)
        data_doacao_str = data.get('data_doacao')
        if data_doacao_str:
            try:
                data_doacao = datetime.strptime(data_doacao_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "message": "Formato de data_doacao inválido. Use YYYY-MM-DD"
                }), 400
        else:
            data_doacao = datetime.now().date()

        historico = HistoricoModel.criar(
            id_usuario=agendamento['id_usuario'],
            id_hemocentro=g.id_hemocentro,
            id_agendamento=id_agendamento,
            quantidade_ml=quantidade_ml,
            tipo_doacao=tipo_doacao,
            proxima_doacao_permitida=proxima_doacao.date(),
            data_doacao=data_doacao,
            observacoes=observacoes
        )

        AgendamentoModel.atualizar(id_agendamento, {'status': 'realizado'})
        if agendamento.get('id_campanha'):
            quantidade_litros = quantidade_ml / 1000.0
            CampanhaModel.incrementar_litros(
                agendamento['id_campanha'], 
                quantidade_litros
            )
        
        return jsonify({
            "success": True,
            "message": "Doação registrada com sucesso!",
            "historico": historico,
            "proxima_doacao_permitida": proxima_doacao.strftime('%Y-%m-%d')
        }), 201
        
    except ValueError as ve:
        return jsonify({
            "success": False,
            "message": str(ve)
        }), 400
    except Exception as e:
        print(f"[ERRO] Registrar doação: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao registrar doação"
        }), 500


# historico e doação (doador)
@historico_bp.route('/minhas-doacoes', methods=['GET'])
@requer_doador
def minhas_doacoes(current_user):
    try:
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
        
        return jsonify({
            "success": True,
            "doacoes": historico,
            "estatisticas": {
                "total_doacoes": total_doacoes,
                "total_ml": total_ml,
                "proxima_doacao_permitida": str(proxima_doacao) if proxima_doacao else None,
                "pode_doar_agora": pode_doar
            }
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Listar minhas doações: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao buscar histórico"
        }), 500


# listar todas doações (colaborador)
@historico_bp.route('/doacoes', methods=['GET'])
@requer_colaborador
def listar_todas_doacoes(current_user):
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        tipo_doacao = request.args.get('tipo_doacao')
        limite = request.args.get('limite', 100, type=int)
        doacoes = HistoricoModel.listar_por_hemocentro(
            id_hemocentro=g.id_hemocentro,
            data_inicio=data_inicio,
            data_fim=data_fim,
            tipo_doacao=tipo_doacao,
            limite=limite
        )
        total_doacoes = len(doacoes)
        total_ml = sum(d.get('quantidade_ml', 0) for d in doacoes)
        por_tipo = {}
        for doacao in doacoes:
            tipo = doacao.get('tipo_doacao', 'desconhecido')
            if tipo not in por_tipo:
                por_tipo[tipo] = {'quantidade': 0, 'total_ml': 0}
            por_tipo[tipo]['quantidade'] += 1
            por_tipo[tipo]['total_ml'] += doacao.get('quantidade_ml', 0)
        
        return jsonify({
            "success": True,
            "doacoes": doacoes,
            "estatisticas": {
                "total": total_doacoes,
                "total_ml": total_ml,
                "por_tipo": por_tipo
            }
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Listar doações: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao listar doações"
        }), 500


# buscar uma doação específica
@historico_bp.route('/doacoes/<int:historico_id>', methods=['GET'])
@token_required
def buscar_doacao(current_user, historico_id):
    try:
        doacao = HistoricoModel.buscar_por_id(historico_id)
        if not doacao:
            return jsonify({
                "success": False,
                "message": "Doação não encontrada"
            }), 404
        if g.tipo_usuario == 'doador':
            if doacao['id_usuario'] != g.id_usuario:
                return jsonify({
                    "success": False,
                    "message": "Você não tem permissão para ver esta doação"
                }), 403
        elif g.tipo_usuario == 'colaborador':
            if doacao['id_hemocentro'] != g.id_hemocentro:
                return jsonify({
                    "success": False,
                    "message": "Você não tem permissão para ver esta doação"
                }), 403
        return jsonify({
            "success": True,
            "doacao": doacao
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Buscar doação: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao buscar doação"
        }), 500

# doadores mais frequentes
@historico_bp.route('/doacoes/doadores-frequentes', methods=['GET'])
@requer_colaborador
def doadores_frequentes(current_user):
    try:
        limite = request.args.get('limite', 10, type=int)
        doadores = HistoricoModel.listar_doadores_frequentes(
            id_hemocentro=g.id_hemocentro,
            limite=limite
        )
        return jsonify({
            "success": True,
            "doadores": doadores,
            "total": len(doadores)
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Doadores frequentes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao buscar doadores"
        }), 500

# campanhas que o doador participou
@historico_bp.route('/minhas-campanhas', methods=['GET'])
@requer_doador
def minhas_campanhas(current_user):
    try:
        campanhas = HistoricoModel.listar_campanhas_participadas(g.id_usuario)
        return jsonify({
            "success": True,
            "campanhas": campanhas,
            "total": len(campanhas)
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Minhas campanhas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao buscar campanhas"
        }), 500