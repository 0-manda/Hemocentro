from flask import Blueprint, request, jsonify, g
from back.models import HorarioFuncionamentoModel, HemocentroModel
from back.utils.auth_utils import requer_colaborador
from datetime import time, datetime

horario_bp = Blueprint('horario_bp', __name__)
# busca hemocentro (só retorna um que tenha no sistema)
def obter_hemocentro_sistema():
    hemocentros = HemocentroModel.listar_ativos()
    return hemocentros[0] if hemocentros else None
# mapeando dias da semana
DIAS_SEMANA_MAP = {
    'domingo': 0, 'dom': 0,
    'segunda': 1, 'segunda-feira': 1, 'seg': 1,
    'terca': 2, 'terça': 2, 'terça-feira': 2, 'ter': 2,
    'quarta': 3, 'quarta-feira': 3, 'qua': 3,
    'quinta': 4, 'quinta-feira': 4, 'qui': 4,
    'sexta': 5, 'sexta-feira': 5, 'sex': 5,
    'sabado': 6, 'sábado': 6, 'sab': 6
}
DIAS_SEMANA_NOMES = [
    'Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira',
    'Quinta-feira', 'Sexta-feira', 'Sábado'
]
DIAS_NUMERO_PARA_NOME = [
    'domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado'
]
def numero_para_dia(numero):
    if 0 <= numero <= 6:
        return DIAS_NUMERO_PARA_NOME[numero]
    raise ValueError(f"Número de dia inválido: {numero}")

# cadastro de horario do hemocentro
@horario_bp.route('/horarios', methods=['POST'])
@requer_colaborador
def cadastrar_horario(current_user):
    try:
        data = request.json or {}
        campos_obrigatorios = ['dia_semana', 'horario_abertura', 'horario_fechamento']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False,
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        dia_input = str(data['dia_semana']).strip().lower()
        if dia_input in DIAS_SEMANA_MAP:
            dia_numero = DIAS_SEMANA_MAP[dia_input]
        elif dia_input.isdigit() and 0 <= int(dia_input) <= 6:
            dia_numero = int(dia_input)
        else:
            return jsonify({
                "success": False,
                "message": "Dia inválido. Use 0-6 ou nome (ex: 'segunda', 'terça')"
            }), 400
        dia_nome_banco = numero_para_dia(dia_numero)
        try:
            hora_abertura = data['horario_abertura'].strip()
            hora_fechamento = data['horario_fechamento'].strip()
            if len(hora_abertura.split(':')) == 2:
                hora_abertura += ':00'
            if len(hora_fechamento.split(':')) == 2:
                hora_fechamento += ':00'
            abertura_time = time.fromisoformat(hora_abertura)
            fechamento_time = time.fromisoformat(hora_fechamento)
            if abertura_time >= fechamento_time:
                return jsonify({
                    "success": False,
                    "message": "Horário de abertura deve ser antes do fechamento"
                }), 400
            horario_abertura = hora_abertura[:5]
            horario_fechamento = hora_fechamento[:5]
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Formato inválido. Use HH:MM (ex: 08:00, 18:00)"
            }), 400
        horario_existente = HorarioFuncionamentoModel.buscar_por_dia(
            id_hemocentro=g.id_hemocentro,
            dia_semana=dia_nome_banco
        )
        if horario_existente:
            return jsonify({
                "success": False,
                "message": f"Já existe horário para {DIAS_SEMANA_NOMES[dia_numero]}"
            }), 409
        horario = HorarioFuncionamentoModel.criar(
            id_hemocentro=g.id_hemocentro,
            dia_semana=dia_nome_banco,
            horario_abertura=horario_abertura,
            horario_fechamento=horario_fechamento,
            observacao=data.get('observacao', '').strip() if data.get('observacao') else None
        )
        return jsonify({
            "success": True,
            "message": f"Horário de {DIAS_SEMANA_NOMES[dia_numero]} cadastrado com sucesso!",
            "horario": horario
        }), 201  
    except ValueError as ve:
        return jsonify({
            "success": False,
            "message": str(ve)
        }), 400
    except Exception as e:
        print(f"[ERRO] Cadastrar horário: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao cadastrar horário"
        }), 500

# listar horários
@horario_bp.route('/horarios', methods=['GET'])
def listar_horarios():
    try:
        hemocentro = obter_hemocentro_sistema()
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        horarios = HorarioFuncionamentoModel.listar_por_hemocentro(
            id_hemocentro=hemocentro['id_hemocentro']
        )
        for horario in horarios:
            dia_nome_banco = horario.get('dia_semana', 'domingo')
            try:
                dia_numero = DIAS_NUMERO_PARA_NOME.index(dia_nome_banco)
                horario['dia_semana_numero'] = dia_numero
                horario['dia_semana_nome'] = DIAS_SEMANA_NOMES[dia_numero]
            except ValueError:
                horario['dia_semana_numero'] = 0
                horario['dia_semana_nome'] = 'Domingo'
        
        return jsonify({
            "success": True,
            "hemocentro": {
                "id_hemocentro": hemocentro['id_hemocentro'],
                "nome": hemocentro['nome']
            },
            "horarios": horarios
        }), 200
    except Exception as e:
        print(f"[ERRO] Listar horários: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao listar horários"
        }), 500

# atualizar horario
@horario_bp.route('/horarios/<int:horario_id>', methods=['PUT'])
@requer_colaborador
def atualizar_horario(current_user, horario_id):
    try:
        data = request.json or {}
        horario = HorarioFuncionamentoModel.buscar_por_id(horario_id)
        if not horario:
            return jsonify({
                "success": False,
                "message": "Horário não encontrado"
            }), 404
        if horario['id_hemocentro'] != g.id_hemocentro:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para editar este horário"
            }), 403
        campos_para_atualizar = {}
        if data.get('horario_abertura'):
            hora = data['horario_abertura'].strip()
            if len(hora.split(':')) == 2:
                hora += ':00'
            try:
                time.fromisoformat(hora)
                campos_para_atualizar['horario_abertura'] = hora[:5]
            except ValueError:
                return jsonify({
                    "success": False,
                    "message": "Formato de abertura inválido"
                }), 400
        if data.get('horario_fechamento'):
            hora = data['horario_fechamento'].strip()
            if len(hora.split(':')) == 2:
                hora += ':00'
            try:
                time.fromisoformat(hora)
                campos_para_atualizar['horario_fechamento'] = hora[:5]
            except ValueError:
                return jsonify({
                    "success": False,
                    "message": "Formato de fechamento inválido"
                }), 400
        abertura = campos_para_atualizar.get('horario_abertura', horario.get('horario_abertura'))
        fechamento = campos_para_atualizar.get('horario_fechamento', horario.get('horario_fechamento'))
        if abertura and fechamento:
            if isinstance(abertura, time):
                abertura = str(abertura)[:5]
            if isinstance(fechamento, time):
                fechamento = str(fechamento)[:5]
            ab = abertura if len(abertura.split(':')) == 3 else abertura + ':00'
            fe = fechamento if len(fechamento.split(':')) == 3 else fechamento + ':00'
            if time.fromisoformat(ab) >= time.fromisoformat(fe):
                return jsonify({
                    "success": False,
                    "message": "Abertura deve ser antes do fechamento"
                }), 400
        if 'observacao' in data:
            campos_para_atualizar['observacao'] = data['observacao'].strip() if data['observacao'] else None
        if 'ativo' in data:
            campos_para_atualizar['ativo'] = bool(data['ativo'])
        if not campos_para_atualizar:
            return jsonify({
                "success": False,
                "message": "Nenhum campo para atualizar"
            }), 400
        sucesso = HorarioFuncionamentoModel.atualizar(horario_id, campos_para_atualizar)
        if not sucesso:
            return jsonify({
                "success": False,
                "message": "Erro ao atualizar horário"
            }), 500
        horario_atualizado = HorarioFuncionamentoModel.buscar_por_id(horario_id)
        dia_nome_banco = horario_atualizado.get('dia_semana', 'domingo')
        try:
            dia_numero = DIAS_NUMERO_PARA_NOME.index(dia_nome_banco)
            horario_atualizado['dia_semana_numero'] = dia_numero
            horario_atualizado['dia_semana_nome'] = DIAS_SEMANA_NOMES[dia_numero]
        except ValueError:
            horario_atualizado['dia_semana_numero'] = 0
            horario_atualizado['dia_semana_nome'] = 'Domingo'
        return jsonify({
            "success": True,
            "message": "Horário atualizado com sucesso!",
            "horario": horario_atualizado
        }), 200   
    except Exception as e:
        print(f"[ERRO] Atualizar horário: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao atualizar horário"
        }), 500

# deletar horario
@horario_bp.route('/horarios/<int:horario_id>', methods=['DELETE'])
@requer_colaborador
def deletar_horario(current_user, horario_id):
    try:
        horario = HorarioFuncionamentoModel.buscar_por_id(horario_id)
        if not horario:
            return jsonify({
                "success": False,
                "message": "Horário não encontrado"
            }), 404
        if horario['id_hemocentro'] != g.id_hemocentro:
            return jsonify({
                "success": False,
                "message": "Você não tem permissão para deletar este horário"
            }), 403
        sucesso = HorarioFuncionamentoModel.deletar(horario_id)
        if not sucesso:
            return jsonify({
                "success": False,
                "message": "Erro ao deletar horário"
            }), 500
        return jsonify({
            "success": True,
            "message": "Horário deletado com sucesso!"
        }), 200      
    except Exception as e:
        print(f"[ERRO] Deletar horário: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao deletar horário"
        }), 500

# verifica se está aberto agora
@horario_bp.route('/horarios/aberto-agora', methods=['GET'])
def esta_aberto_agora():
    try:
        hemocentro = obter_hemocentro_sistema()
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        agora = datetime.now()
        dia_atual = agora.weekday()
        dia_atual = (dia_atual + 1) % 7
        dia_nome_banco = numero_para_dia(dia_atual)
        horario_hoje = HorarioFuncionamentoModel.buscar_por_dia(
            id_hemocentro=hemocentro['id_hemocentro'],
            dia_semana=dia_nome_banco
        )
        if not horario_hoje or not horario_hoje.get('ativo', False):
            return jsonify({
                "success": True,
                "aberto": False,
                "mensagem": f"Fechado hoje ({DIAS_SEMANA_NOMES[dia_atual]})"
            }), 200
        hora_atual = agora.time()
        abertura = horario_hoje['horario_abertura']
        fechamento = horario_hoje['horario_fechamento']
        if isinstance(abertura, str):
            if len(abertura.split(':')) == 2:
                abertura += ':00'
            abertura = time.fromisoformat(abertura)
        if isinstance(fechamento, str):
            if len(fechamento.split(':')) == 2:
                fechamento += ':00'
            fechamento = time.fromisoformat(fechamento)
        esta_aberto = abertura <= hora_atual <= fechamento
        return jsonify({
            "success": True,
            "aberto": esta_aberto,
            "horario_hoje": {
                "dia": DIAS_SEMANA_NOMES[dia_atual],
                "abertura": str(abertura)[:5],
                "fechamento": str(fechamento)[:5]
            },
            "mensagem": "Aberto agora!" if esta_aberto else f"Fechado (Abre às {str(abertura)[:5]})"
        }), 200
    except Exception as e:
        print(f"[ERRO] Verificar abertura: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao verificar status"
        }), 500

# horario colaborador
@horario_bp.route('/meus-horarios', methods=['GET'])
@requer_colaborador
def meus_horarios(current_user):
    try:
        horarios = HorarioFuncionamentoModel.listar_por_hemocentro(
            id_hemocentro=g.id_hemocentro
        )
        for horario in horarios:
            dia_nome_banco = horario.get('dia_semana', 'domingo')
            try:
                dia_numero = DIAS_NUMERO_PARA_NOME.index(dia_nome_banco)
                horario['dia_semana_numero'] = dia_numero
                horario['dia_semana_nome'] = DIAS_SEMANA_NOMES[dia_numero]
            except ValueError:
                horario['dia_semana_numero'] = 0
                horario['dia_semana_nome'] = 'Domingo'
        return jsonify({
            "success": True,
            "horarios": horarios,
            "total": len(horarios)
        }), 200 
    except Exception as e:
        print(f"[ERRO] Listar meus horários: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao listar horários"
        }), 500