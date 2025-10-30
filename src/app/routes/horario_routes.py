from flask import Blueprint, request, jsonify
from models.models import HorarioFuncionamentoModel, HemocentroModel, UsuarioModel
from utils.auth_utils import token_required, hemocentro_required, only_numbers
from datetime import time

horario_bp = Blueprint('horario', __name__)


# ===== CADASTRAR HORÁRIO (HEMOCENTRO) =====

@horario_bp.route('/horarios', methods=['POST'])
@token_required
@hemocentro_required
def cadastrar_horario(current_user):
    try:
        data = request.json or {}
        
        # ===== CAMPOS OBRIGATÓRIOS =====
        campos_obrigatorios = ['dia_semana', 'horario_abertura', 'horario_fechamento']
        
        for campo in campos_obrigatorios:
            if campo not in data or data.get(campo) is None:
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório: {campo}"
                }), 400
        
        # ===== BUSCA HEMOCENTRO DO USUÁRIO LOGADO =====
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado."
            }), 404
        
        hemocentro_id = hemocentro['hemocentro_id']
        
        # ===== VALIDAÇÃO: DIA DA SEMANA =====
        dia_semana = str(data['dia_semana']).strip().lower()
        
        # Mapeamento de nomes para números
        dias_map = {
            'domingo': 0, 'dom': 0,
            'segunda': 1, 'segunda-feira': 1, 'seg': 1,
            'terca': 2, 'terça': 2, 'terça-feira': 2, 'ter': 2,
            'quarta': 3, 'quarta-feira': 3, 'qua': 3,
            'quinta': 4, 'quinta-feira': 4, 'qui': 4,
            'sexta': 5, 'sexta-feira': 5, 'sex': 5,
            'sabado': 6, 'sábado': 6, 'sab': 6
        }
        
        # Aceita número (0-6) ou nome
        if dia_semana in dias_map:
            dia_numero = dias_map[dia_semana]
        elif dia_semana.isdigit() and 0 <= int(dia_semana) <= 6:
            dia_numero = int(dia_semana)
        else:
            return jsonify({
                "success": False,
                "message": "Dia da semana inválido. Use 0-6 ou nome (ex: 'segunda', 'terça')."
            }), 400
        
        # ===== VALIDAÇÃO: HORÁRIOS =====
        try:
            # Formato esperado: "HH:MM" ou "HH:MM:SS"
            hora_abertura = data['horario_abertura'].strip()
            hora_fechamento = data['horario_fechamento'].strip()
            
            # Converte para objeto time para validar
            if len(hora_abertura.split(':')) == 2:
                hora_abertura += ':00'
            if len(hora_fechamento.split(':')) == 2:
                hora_fechamento += ':00'
            
            abertura_time = time.fromisoformat(hora_abertura)
            fechamento_time = time.fromisoformat(hora_fechamento)
            
            # Validação: abertura < fechamento
            if abertura_time >= fechamento_time:
                return jsonify({
                    "success": False,
                    "message": "Horário de abertura deve ser anterior ao de fechamento."
                }), 400
            
            # Remove segundos para armazenar apenas HH:MM
            horario_abertura = hora_abertura[:5]
            horario_fechamento = hora_fechamento[:5]
            
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Formato de horário inválido. Use HH:MM (ex: 08:00, 18:00)."
            }), 400
        
        # ===== VERIFICAR DUPLICAÇÃO =====
        horario_existente = HorarioFuncionamentoModel.buscar_por_hemocentro_e_dia(
            hemocentro_id, dia_numero
        )
        
        if horario_existente:
            return jsonify({
                "success": False,
                "message": f"Já existe um horário cadastrado para este dia da semana."
            }), 409
        
        # ===== CRIAÇÃO DO HORÁRIO =====
        horario_id = HorarioFuncionamentoModel.criar_horario(
            hemocentro_id=hemocentro_id,  # Do token, não do request
            dia_semana=dia_numero,
            horario_abertura=horario_abertura,
            horario_fechamento=horario_fechamento,
            observacao=data.get('observacao', '').strip(),  # Opcional
            ativo=data.get('ativo', True)  # Padrão: True
        )
        
        return jsonify({
            "success": True,
            "message": "Horário cadastrado com sucesso!",
            "horario_id": horario_id
        }), 201
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": f"Erro de validação: {str(e)}"
        }), 400
    except Exception as e:
        print(f"Erro ao cadastrar horário: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== LISTAR HORÁRIOS DO HEMOCENTRO (PÚBLICO) =====

@horario_bp.route('/horarios/<int:hemocentro_id>', methods=['GET'])
def listar_horarios(hemocentro_id):
    """
    NOVO: Lista horários de funcionamento de um hemocentro
    MOTIVO: Doadores precisam ver quando o hemocentro abre
    
    PÚBLICO: Não requer autenticação
    """
    try:
        # Verifica se hemocentro existe
        hemocentro = HemocentroModel.buscar_por_id(hemocentro_id)
        
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado."
            }), 404
        
        # Lista horários
        horarios = HorarioFuncionamentoModel.listar_por_hemocentro(hemocentro_id)
        
        # Mapeia números para nomes de dias
        dias_semana = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 
                       'Quinta-feira', 'Sexta-feira', 'Sábado']
        
        # Adiciona nome do dia
        for horario in horarios:
            horario['dia_semana_nome'] = dias_semana[horario['dia_semana']]
        
        return jsonify({
            "success": True,
            "horarios": horarios
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar horários: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== LISTAR MEUS HORÁRIOS (HEMOCENTRO) =====

@horario_bp.route('/meus-horarios', methods=['GET'])
@token_required
@hemocentro_required
def meus_horarios(current_user):
    """
    NOVO: Lista horários do hemocentro logado
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
        
        # Lista horários (incluindo inativos)
        horarios = HorarioFuncionamentoModel.listar_por_hemocentro(
            hemocentro['hemocentro_id'], 
            incluir_inativos=True
        )
        
        # Adiciona nomes dos dias
        dias_semana = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 
                       'Quinta-feira', 'Sexta-feira', 'Sábado']
        
        for horario in horarios:
            horario['dia_semana_nome'] = dias_semana[horario['dia_semana']]
        
        return jsonify({
            "success": True,
            "horarios": horarios
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar horários: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== ATUALIZAR HORÁRIO =====

@horario_bp.route('/horarios/<int:horario_id>', methods=['PUT'])
@token_required
@hemocentro_required
def atualizar_horario(current_user, horario_id):
    """
    NOVO: Atualiza horário de funcionamento
    MOTIVO: Editar horários
    
    SEGURANÇA: Só pode editar horários do próprio hemocentro
    """
    try:
        data = request.json or {}
        
        # Busca horário
        horario = HorarioFuncionamentoModel.buscar_por_id(horario_id)
        
        if not horario:
            return jsonify({
                "success": False,
                "message": "Horário não encontrado."
            }), 404
        
        # SEGURANÇA: Verifica se pertence ao hemocentro do usuário
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        
        if horario['hemocentro_id'] != hemocentro['hemocentro_id']:
            return jsonify({
                "success": False,
                "message": "Você só pode editar horários do seu hemocentro."
            }), 403
        
        # Campos editáveis
        campos_para_atualizar = {}
        
        if 'horario_abertura' in data:
            campos_para_atualizar['horario_abertura'] = data['horario_abertura']
        
        if 'horario_fechamento' in data:
            campos_para_atualizar['horario_fechamento'] = data['horario_fechamento']
        
        if 'observacao' in data:
            campos_para_atualizar['observacao'] = data['observacao']
        
        if 'ativo' in data:
            campos_para_atualizar['ativo'] = data['ativo']
        
        if not campos_para_atualizar:
            return jsonify({
                "success": False,
                "message": "Nenhum campo para atualizar."
            }), 400
        
        # Validação de horários (se fornecidos)
        if 'horario_abertura' in campos_para_atualizar or 'horario_fechamento' in campos_para_atualizar:
            abertura = campos_para_atualizar.get('horario_abertura', horario['horario_abertura'])
            fechamento = campos_para_atualizar.get('horario_fechamento', horario['horario_fechamento'])
            
            try:
                # Adiciona segundos se necessário
                if isinstance(abertura, str) and len(abertura.split(':')) == 2:
                    abertura += ':00'
                if isinstance(fechamento, str) and len(fechamento.split(':')) == 2:
                    fechamento += ':00'
                
                abertura_time = time.fromisoformat(str(abertura))
                fechamento_time = time.fromisoformat(str(fechamento))
                
                if abertura_time >= fechamento_time:
                    return jsonify({
                        "success": False,
                        "message": "Horário de abertura deve ser anterior ao de fechamento."
                    }), 400
            except ValueError:
                return jsonify({
                    "success": False,
                    "message": "Formato de horário inválido. Use HH:MM."
                }), 400
        
        # Atualiza
        HorarioFuncionamentoModel.atualizar(horario_id, campos_para_atualizar)
        
        return jsonify({
            "success": True,
            "message": "Horário atualizado com sucesso!"
        }), 200
        
    except Exception as e:
        print(f"Erro ao atualizar horário: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== DELETAR HORÁRIO =====

@horario_bp.route('/horarios/<int:horario_id>', methods=['DELETE'])
@token_required
@hemocentro_required
def deletar_horario(current_user, horario_id):
    """
    NOVO: Deleta horário de funcionamento
    MOTIVO: Remover horário (ex: fechado aos domingos)
    
    SEGURANÇA: Só pode deletar horários do próprio hemocentro
    """
    try:
        # Busca horário
        horario = HorarioFuncionamentoModel.buscar_por_id(horario_id)
        
        if not horario:
            return jsonify({
                "success": False,
                "message": "Horário não encontrado."
            }), 404
        
        # SEGURANÇA: Verifica permissão
        usuario = UsuarioModel.buscar_por_id(current_user['usuario_id'])
        cnpj = only_numbers(usuario['cpf_cnpj'])
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
        
        if horario['hemocentro_id'] != hemocentro['hemocentro_id']:
            return jsonify({
                "success": False,
                "message": "Você só pode deletar horários do seu hemocentro."
            }), 403
        
        # Deleta
        HorarioFuncionamentoModel.deletar(horario_id)
        
        return jsonify({
            "success": True,
            "message": "Horário deletado com sucesso!"
        }), 200
        
    except Exception as e:
        print(f"Erro ao deletar horário: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500