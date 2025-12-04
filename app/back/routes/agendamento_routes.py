from flask import Blueprint, request, jsonify, g
from back.models import AgendamentoModel, HemocentroModel, CampanhaModel, UsuarioModel
from back.utils.auth_utils import requer_doador, requer_colaborador
from datetime import datetime, timezone, timedelta

agendamento_bp = Blueprint('agendamento_bp', __name__)

# criar agendamento
@agendamento_bp.route('/agendamentos', methods=['POST'])
@requer_doador
def criar_agendamento(current_user):
    try:
        data = request.json or {}
        campos_obrigatorios = ['id_hemocentro', 'data_hora', 'tipo_sangue']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        try:
            data_hora_str = data['data_hora'].replace('Z', '+00:00')
            data_agendamento = datetime.fromisoformat(data_hora_str)
            if data_agendamento.tzinfo is None:
                data_agendamento = data_agendamento.replace(tzinfo=timezone.utc)
            data_hora_mysql = data_agendamento.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            agora = datetime.now(timezone.utc)
            if data_agendamento <= agora:
                return jsonify({
                    "success": False,
                    "message": "A data do agendamento deve ser futura"
                }), 400
            minimo = agora + timedelta(hours=24)
            if data_agendamento < minimo:
                return jsonify({
                    "success": False,
                    "message": "Agendamento deve ser feito com no mínimo 24 horas de antecedência"
                }), 400
            maximo = agora + timedelta(days=180)
            if data_agendamento > maximo:
                return jsonify({
                    "success": False,
                    "message": "Agendamento não pode ser feito com mais de 6 meses de antecedência"
                }), 400    
        except (ValueError, AttributeError) as e:
            return jsonify({
                "success": False,
                "message": "Formato de data inválido. Use ISO 8601 (ex: 2025-12-25T14:30:00Z)"
            }), 400
        tipos_sangue_validos = ['sangue_total', 'plaquetas', 'plasma', 'aferese']
        tipo_sangue = data['tipo_sangue'].lower()
        
        if tipo_sangue not in tipos_sangue_validos:
            return jsonify({
                "success": False,
                "message": f"Tipo de sangue inválido. Valores aceitos: {', '.join(tipos_sangue_validos)}"
            }), 400
        hemocentro = HemocentroModel.buscar_por_id(data['id_hemocentro'])
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        if not hemocentro.get('ativo', False):
            return jsonify({
                "success": False,
                "message": "Este hemocentro está temporariamente desativado"
            }), 400
        id_campanha = data.get('id_campanha')
        if id_campanha:
            campanha = CampanhaModel.buscar_por_id(id_campanha)
            if not campanha:
                return jsonify({
                    "success": False,
                    "message": "Campanha não encontrada"
                }), 404
            
            if not campanha.get('ativa', False):
                return jsonify({
                    "success": False,
                    "message": "Esta campanha não está mais ativa"
                }), 400
        usuario = g.current_user
        if usuario.get('data_nascimento'):
            data_nasc = usuario['data_nascimento']
            if isinstance(data_nasc, str):
                data_nasc = datetime.fromisoformat(data_nasc).date()
            idade = (datetime.now().date() - data_nasc).days // 365
            if idade < 16:
                return jsonify({
                    "success": False,
                    "message": "Você deve ter no mínimo 16 anos para doar sangue"
                }), 400
            if idade > 69:
                return jsonify({
                    "success": False,
                    "message": "A doação de sangue é permitida até os 69 anos"
                }), 400
        ultima_doacao = AgendamentoModel.buscar_ultima_doacao_realizada(g.id_usuario)
        if ultima_doacao:
            ultima_data = ultima_doacao.get('data_hora')
            if isinstance(ultima_data, str):
                ultima_data = datetime.fromisoformat(ultima_data.replace('Z', '+00:00'))
            dias_desde_ultima = (data_agendamento - ultima_data).day
            if tipo_sangue == 'sangue_total':
                intervalo_minimo = 75
                tipo_intervalo = "sangue total"
            elif tipo_sangue in ['plaquetas', 'plasma']:
                intervalo_minimo = 2
                tipo_intervalo = tipo_sangue
            else:
                intervalo_minimo = 7
                tipo_intervalo = "aférese"
            if dias_desde_ultima < intervalo_minimo:
                dias_faltando = intervalo_minimo - dias_desde_ultima
                return jsonify({
                    "success": False,
                    "message": f"Intervalo mínimo entre doações de {tipo_intervalo} não respeitado. Aguarde {dias_faltando} dias",
                    "proxima_doacao_permitida": (ultima_data + timedelta(days=intervalo_minimo)).isoformat()
                }), 400
        agendamentos_existentes = AgendamentoModel.listar_por_usuario(
            id_usuario=g.id_usuario,
            status='pendente'
        )
        for ag in agendamentos_existentes:
            ag_data = ag.get('data_hora')
            if isinstance(ag_data, str):
                ag_data = datetime.fromisoformat(ag_data.replace('Z', '+00:00'))
            
            if (ag_data.date() == data_agendamento.date() and 
                ag.get('id_hemocentro') == data['id_hemocentro']):
                return jsonify({
                    "success": False,
                    "message": "Você já possui um agendamento pendente para este dia neste hemocentro"
                }), 400
            
        agendamento = AgendamentoModel.criar(
            id_usuario=g.id_usuario,
            id_hemocentro=data['id_hemocentro'],
            data_hora=data_hora_mysql,
            tipo_sangue_doado=tipo_sangue,
            id_campanha=id_campanha,
            status='pendente',
            observacoes=data.get('observacoes', '').strip() if data.get('observacoes') else None
        )
        
        return jsonify({
            "success": True, 
            "message": "Agendamento criado com sucesso! Aguarde a confirmação do hemocentro.",
            "agendamento": agendamento
        }), 201
        
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 400
    except Exception as e:
        print(f"[ERRO] Criar agendamento: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "message": "Erro interno ao criar agendamento"
        }), 500

# listar agendamentos do usuário
@agendamento_bp.route('/meus-agendamentos', methods=['GET'])
@requer_doador
def listar_meus_agendamentos(current_user):
    try:
        status = request.args.get('status')
        apenas_futuros = request.args.get('futuro', 'false').lower() == 'true'
        agendamentos = AgendamentoModel.listar_por_usuario(
            id_usuario=g.id_usuario,
            status=status
        )
        if apenas_futuros:
            agora = datetime.now() 
            agendamentos_futuros = []
            for ag in agendamentos:
                data_do_banco = ag['data_hora']
                if isinstance(data_do_banco, str):
                    data_do_banco = datetime.fromisoformat(str(data_do_banco))
                if data_do_banco > agora:
                    agendamentos_futuros.append(ag)
            
            agendamentos = agendamentos_futuros
        return jsonify({
            "success": True,
            "total": len(agendamentos),
            "agendamentos": agendamentos
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Listar agendamentos: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao buscar agendamentos"
        }), 500

# cancelar agendamento
@agendamento_bp.route('/agendamentos/<int:id_agendamento>', methods=['DELETE'])
@requer_doador
def cancelar_agendamento(current_user, id_agendamento):
    try:
        agendamento = AgendamentoModel.buscar_por_id(id_agendamento)
        if not agendamento:
            return jsonify({
                "success": False,
                "message": "Agendamento não encontrado"
            }), 404
        if agendamento['id_usuario'] != g.id_usuario:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para cancelar este agendamento"
            }), 403
        status_atual = agendamento.get('status', '').lower()
        if status_atual not in ['pendente', 'confirmado']:
            return jsonify({
                "success": False,
                "message": f"Agendamentos com status '{status_atual}' não podem ser cancelados"
            }), 400
        sucesso = AgendamentoModel.atualizar(id_agendamento, {'status': 'cancelado'})
        if not sucesso:
            return jsonify({
                "success": False,
                "message": "Erro ao cancelar agendamento"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "Agendamento cancelado com sucesso"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Cancelar agendamento: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao cancelar agendamento"
        }), 500


# listar todos os agendamentos colaborador
@agendamento_bp.route('/agendamentos', methods=['GET'])
@requer_colaborador
def listar_todos_agendamentos(current_user):
    try:
        status = request.args.get('status')
        data_inicio_str = request.args.get('data_inicio')
        data_inicio = None
        if data_inicio_str:
            try:
                data_inicio = datetime.fromisoformat(data_inicio_str).date()
            except ValueError:
                return jsonify({
                    "success": False,
                    "message": "Formato de data_inicio inválido. Use YYYY-MM-DD"
                }), 400
        agendamentos = AgendamentoModel.listar_todos(
            status=status,
            id_hemocentro=g.id_hemocentro,
            data_inicio=data_inicio
        )
        return jsonify({
            "success": True,
            "total": len(agendamentos),
            "agendamentos": agendamentos
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Listar todos agendamentos: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao buscar agendamentos"
        }), 500

# ===== NOVOS ENDPOINTS PARA COLABORADOR GERENCIAR AGENDAMENTOS =====

# confirmar agendamento
@agendamento_bp.route('/agendamentos/<int:id_agendamento>/confirmar', methods=['PATCH'])
@requer_colaborador
def confirmar_agendamento(current_user, id_agendamento):
    try:
        agendamento = AgendamentoModel.buscar_por_id(id_agendamento)
        if not agendamento:
            return jsonify({
                "success": False,
                "message": "Agendamento não encontrado"
            }), 404
        
        if agendamento.get('id_hemocentro') != g.id_hemocentro:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para gerenciar este agendamento"
            }), 403
        
        if agendamento.get('status') != 'pendente':
            return jsonify({
                "success": False,
                "message": f"Apenas agendamentos pendentes podem ser confirmados. Status atual: {agendamento.get('status')}"
            }), 400
        
        sucesso = AgendamentoModel.atualizar(id_agendamento, {'status': 'confirmado'})
        if not sucesso:
            return jsonify({
                "success": False,
                "message": "Erro ao confirmar agendamento"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "Agendamento confirmado com sucesso"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Confirmar agendamento: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao confirmar agendamento"
        }), 500

# marcar agendamento como realizado
@agendamento_bp.route('/agendamentos/<int:id_agendamento>/realizar', methods=['PATCH'])
@requer_colaborador
def marcar_realizado(current_user, id_agendamento):
    try:
        from back.models import HistoricoModel  # Importar o model de histórico
        
        agendamento = AgendamentoModel.buscar_por_id(id_agendamento)
        if not agendamento:
            return jsonify({
                "success": False,
                "message": "Agendamento não encontrado"
            }), 404
        
        if agendamento.get('id_hemocentro') != g.id_hemocentro:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para gerenciar este agendamento"
            }), 403
        
        # Permite marcar como realizado agendamentos pendentes ou confirmados
        status_atual = agendamento.get('status', '').lower()
        if status_atual not in ['pendente', 'confirmado']:
            return jsonify({
                "success": False,
                "message": f"Apenas agendamentos pendentes ou confirmados podem ser marcados como realizados. Status atual: {status_atual}"
            }), 400
        
        # Verificar se já existe doação registrada para este agendamento
        doacao_existente = HistoricoModel.buscar_por_agendamento(id_agendamento)
        if doacao_existente:
            return jsonify({
                "success": False,
                "message": "Doação já foi registrada para este agendamento"
            }), 409
        
        # 1️⃣ ⭐ CRIAR REGISTRO NO HISTÓRICO DE DOAÇÕES ⭐
        try:
            # Calcular próxima doação permitida
            tipo_doacao = agendamento.get('tipo_sangue_doado', 'sangue_total')
            agora = datetime.now()
            
            if tipo_doacao == 'sangue_total':
                proxima_doacao = agora + timedelta(days=75)
            elif tipo_doacao in ['plaquetas', 'plasma']:
                proxima_doacao = agora + timedelta(days=2)
            elif tipo_doacao == 'aferese':
                proxima_doacao = agora + timedelta(days=7)
            else:
                proxima_doacao = agora + timedelta(days=60)
            
            # Quantidade padrão de sangue coletado (pode ser parametrizado depois)
            quantidade_ml = 450
            
            # Criar registro no histórico
            historico = HistoricoModel.criar(
                id_usuario=agendamento['id_usuario'],
                id_hemocentro=g.id_hemocentro,
                id_agendamento=id_agendamento,
                quantidade_ml=quantidade_ml,
                tipo_doacao=tipo_doacao,
                proxima_doacao_permitida=proxima_doacao.date(),
                data_doacao=datetime.now().date(),
                observacoes=agendamento.get('observacoes')
            )
            
            print(f"[INFO] Histórico criado com sucesso: {historico}")
            
        except Exception as e_historico:
            print(f"[ERRO] Falha ao criar histórico: {str(e_historico)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "message": f"Erro ao registrar doação no histórico: {str(e_historico)}"
            }), 500
        
        # 2️⃣ Atualizar status do agendamento
        sucesso = AgendamentoModel.atualizar(id_agendamento, {'status': 'realizado'})
        if not sucesso:
            print("[ERRO] Falha ao atualizar status do agendamento")
            return jsonify({
                "success": False,
                "message": "Erro ao atualizar status do agendamento"
            }), 500
        
        # 3️⃣ Se houver campanha, incrementar o contador
        if agendamento.get('id_campanha'):
            try:
                quantidade_litros = quantidade_ml / 1000.0
                CampanhaModel.incrementar_litros(
                    agendamento['id_campanha'], 
                    quantidade_litros
                )
                print(f"[INFO] Campanha {agendamento['id_campanha']} atualizada: +{quantidade_litros}L")
            except Exception as e_campanha:
                print(f"[AVISO] Erro ao atualizar campanha: {str(e_campanha)}")
                # Não falha a operação se não conseguir atualizar campanha
        
        return jsonify({
            "success": True,
            "message": "Doação registrada com sucesso!",
            "historico": historico,
            "proxima_doacao_permitida": proxima_doacao.strftime('%Y-%m-%d')
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Marcar como realizado: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao registrar doação"
        }), 500

# marcar agendamento como não realizado (falta do doador)
@agendamento_bp.route('/agendamentos/<int:id_agendamento>/nao-compareceu', methods=['PATCH'])
@requer_colaborador
def marcar_nao_compareceu(current_user, id_agendamento):
    try:
        agendamento = AgendamentoModel.buscar_por_id(id_agendamento)
        if not agendamento:
            return jsonify({
                "success": False,
                "message": "Agendamento não encontrado"
            }), 404
        
        if agendamento.get('id_hemocentro') != g.id_hemocentro:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para gerenciar este agendamento"
            }), 403
        
        status_atual = agendamento.get('status', '').lower()
        if status_atual not in ['pendente', 'confirmado']:
            return jsonify({
                "success": False,
                "message": f"Apenas agendamentos pendentes ou confirmados podem ser marcados como não compareceu. Status atual: {status_atual}"
            }), 400
        
        sucesso = AgendamentoModel.atualizar(id_agendamento, {'status': 'nao_compareceu'})
        if not sucesso:
            return jsonify({
                "success": False,
                "message": "Erro ao atualizar agendamento"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "Agendamento marcado como não compareceu"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Marcar não compareceu: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao atualizar agendamento"
        }), 500