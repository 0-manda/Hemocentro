from flask import Blueprint, request, jsonify, g
from back.utils.auth_utils import requer_colaborador, only_numbers, validar_email, validar_telefone, is_cnpj
from back.utils.aprovacao_service import criar_solicitacao_aprovacao
from back.models import HemocentroModel

hemocentro_bp = Blueprint('hemocentro_bp', __name__)

def validar_cep(cep):
    cep_limpo = only_numbers(cep)
    return len(cep_limpo) == 8

def validar_estado(estado):
    estados_validos = ['SP']
    return estado.upper() in estados_validos

@hemocentro_bp.route('/cadastrar-hemocentro', methods=['POST'])
def cadastrar_novo_hemocentro():
   #hemocentro é criado como INATIVO e aguarda aprovação do admin.
    try:
        data = request.json or {}
        campos_obrigatorios = ['nome', 'email', 'telefone', 'cnpj', 'endereco', 'cidade', 'estado', 'cep']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False,
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        
        # limpeza de dados
        nome = data['nome'].strip()
        email = data['email'].strip().lower()
        telefone = only_numbers(data['telefone'])
        cnpj = only_numbers(data['cnpj'])
        endereco = data['endereco'].strip()
        cidade = data['cidade'].strip()
        estado = data['estado'].strip().upper()
        cep = only_numbers(data['cep'])
        site = data.get('site', '').strip() if data.get('site') else None
        
        # validações
        if len(nome) < 3:
            return jsonify({
                "success": False,
                "message": "Nome deve ter no mínimo 3 caracteres"
            }), 400
        
        if not validar_email(email):
            return jsonify({
                "success": False,
                "message": "Email inválido"
            }), 400
        
        if HemocentroModel.buscar_por_email(email):
            return jsonify({
                "success": False,
                "message": "Este email já está cadastrado"
            }), 409
        
        if not is_cnpj(cnpj):
            return jsonify({
                "success": False,
                "message": "CNPJ inválido"
            }), 400
        
        if HemocentroModel.buscar_por_cnpj(cnpj):
            return jsonify({
                "success": False,
                "message": "Este CNPJ já está cadastrado"
            }), 409
        
        if not validar_telefone(telefone):
            return jsonify({
                "success": False,
                "message": "Telefone inválido. Use formato: (XX) XXXXX-XXXX"
            }), 400
        
        if len(cep) != 8:
            return jsonify({
                "success": False,
                "message": "CEP inválido. Deve ter 8 dígitos"
            }), 400
        
        if estado != 'SP':
            return jsonify({
                "success": False,
                "message": "Apenas hemocentros de São Paulo são aceitos no MVP"
            }), 400
        
        # Criar hemocentro (será criado como INATIVO, aguardando aprovação)
        hemocentro = HemocentroModel.criar_hemocentro(
            nome=nome,
            cnpj=cnpj,
            email=email,
            telefone=telefone,
            endereco=endereco,
            cidade=cidade,
            estado=estado,
            cep=cep,
            site=site
        )
        
        # Enviar email de solicitação de aprovação para o admin
        from config.config import Config
        email_admin = Config.EMAIL_ADMIN
        
        if email_admin:
            sucesso_email = criar_solicitacao_aprovacao(
            tipo='hemocentro',
            id_entidade=hemocentro['id_hemocentro'],
            email_destino=email_admin,
            dados_entidade={
                'nome': hemocentro['nome'],
                'email': hemocentro['email'],
                'cnpj': hemocentro['cnpj'],
                'endereco': hemocentro.get('endereco'),
                'cidade': hemocentro.get('cidade')
            }
        )
            
            if not sucesso_email:
                print(f"[AVISO] Falha ao enviar email de aprovação para {email_admin}")
        else:
            print("[AVISO] Email do admin não configurado (EMAIL_ADMIN)")
        
        return jsonify({
            "success": True,
            "message": "Cadastro realizado com sucesso! Sua solicitação está aguardando aprovação do administrador. Você receberá um email quando for aprovado.",
            "hemocentro": {
                "id_hemocentro": hemocentro['id_hemocentro'],
                "nome": hemocentro['nome'],
                "email": hemocentro['email'],
                "telefone": hemocentro['telefone'],
                "cnpj": hemocentro['cnpj'],
                "endereco": hemocentro['endereco'],
                "cidade": hemocentro['cidade'],
                "estado": hemocentro['estado'],
                "cep": hemocentro.get('cep'),
                "ativo": False,  #aguardando aprovação
                "data_cadastro": hemocentro['data_cadastro'].isoformat() if hemocentro.get('data_cadastro') else None
            },
            "aguardando_aprovacao": True
        }), 201
        
    except ValueError as ve:
        return jsonify({
            "success": False,
            "message": str(ve)
        }), 400
    except Exception as e:
        print(f"[ERRO] Cadastrar hemocentro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro interno ao cadastrar hemocentro"
        }), 500

# listar hemocentros COM HORÁRIOS
@hemocentro_bp.route('/hemocentros', methods=['GET'])
def listar_hemocentros():
    try:
        from back.models import HorarioFuncionamentoModel
        from datetime import datetime, time, timedelta
        
        hemocentros = HemocentroModel.listar_ativos()
        
        # Adicionar horários para cada hemocentro
        for hemo in hemocentros:
            # Buscar horários
            horarios = HorarioFuncionamentoModel.listar_por_hemocentro(
                id_hemocentro=hemo['id_hemocentro'],
                incluir_inativos=False
            )
            
            # Mapear dias da semana
            DIAS_NUMERO_PARA_NOME = [
                'domingo', 'segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado'
            ]
            DIAS_SEMANA_NOMES = [
                'Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira',
                'Quinta-feira', 'Sexta-feira', 'Sábado'
            ]
            
            # Formatar horários
            horarios_formatados = []
            for horario in horarios:
                dia_nome_banco = horario.get('dia_semana', 'domingo')
                try:
                    dia_numero = DIAS_NUMERO_PARA_NOME.index(dia_nome_banco)
                    horario['dia_semana_numero'] = dia_numero
                    horario['dia_semana_nome'] = DIAS_SEMANA_NOMES[dia_numero]
                except ValueError:
                    horario['dia_semana_numero'] = 0
                    horario['dia_semana_nome'] = 'Domingo'
                
                # Converter timedelta para string no formato "HH:MM:SS"
                if isinstance(horario.get('horario_abertura'), timedelta):
                    total_seconds = int(horario['horario_abertura'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    horario['horario_abertura'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                if isinstance(horario.get('horario_fechamento'), timedelta):
                    total_seconds = int(horario['horario_fechamento'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    horario['horario_fechamento'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                
                horarios_formatados.append(horario)
            
            # Ordenar por dia da semana
            horarios_formatados.sort(key=lambda x: x.get('dia_semana_numero', 0))
            hemo['horarios'] = horarios_formatados
            
            # Verificar se está aberto agora
            agora = datetime.now()
            dia_atual = (agora.weekday() + 1) % 7  # Converter para 0=domingo
            hora_atual = agora.time()
            
            hemo['aberto_agora'] = False
            for h in horarios_formatados:
                if h.get('dia_semana_numero') == dia_atual and h.get('ativo', False):
                    abertura = h['horario_abertura']
                    fechamento = h['horario_fechamento']
                    
                    # Converter strings para time se necessário
                    if isinstance(abertura, str):
                        if len(abertura.split(':')) == 2:
                            abertura += ':00'
                        abertura = time.fromisoformat(abertura)
                    
                    if isinstance(fechamento, str):
                        if len(fechamento.split(':')) == 2:
                            fechamento += ':00'
                        fechamento = time.fromisoformat(fechamento)
                    
                    if abertura <= hora_atual <= fechamento:
                        hemo['aberto_agora'] = True
                        break
        
        return jsonify({
            "success": True,
            "hemocentros": hemocentros,
            "total": len(hemocentros)
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Listar hemocentros: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao listar hemocentros"
        }), 500

# buscar hemocentro por cnpj
# @hemocentro_bp.route('/hemocentros/<cnpj>', methods=['GET'])
# def buscar_hemocentro(cnpj):
#     try:
#         if not is_cnpj(cnpj):
#             return jsonify({
#                 "success": False,
#                 "message": "CNPJ inválido"
#             }), 400
#         hemocentro = HemocentroModel.buscar_por_cnpj(cnpj)
#         if not hemocentro:
#             return jsonify({
#                 "success": False,
#                 "message": "Hemocentro não encontrado"
#             }), 404
        
#         return jsonify({
#             "success": True,
#             "hemocentro": hemocentro
#         }), 200
        
#     except Exception as e:
#         print(f"[ERRO] Buscar hemocentro: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False,
#             "message": "Erro ao buscar hemocentro"
#         }), 500

#atualiza hemocentro
@hemocentro_bp.route('/hemocentros/<cnpj>', methods=['PUT'])
@requer_colaborador
def atualizar_hemocentro(current_user, cnpj):
    try:
        data = request.json or {}
        if not is_cnpj(cnpj):
            return jsonify({
                "success": False,
                "message": "CNPJ inválido"
            }), 400
        
        cnpj_limpo = only_numbers(cnpj)
        cnpj_colaborador = g.hemocentro.get('cnpj')
        if cnpj_limpo != cnpj_colaborador:
            return jsonify({
                "success": False,
                "message": "Você só pode atualizar informações do seu próprio hemocentro"
            }), 403
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj_limpo)
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        
        campos_para_atualizar = {}
        if data.get('nome'):
            nome = data['nome'].strip()
            if len(nome) < 3:
                return jsonify({
                    "success": False, 
                    "message": "Nome deve ter pelo menos 3 caracteres"
                }), 400
            if len(nome) > 200:
                return jsonify({
                    "success": False, 
                    "message": "Nome muito longo (máximo 200 caracteres)"
                }), 400
            campos_para_atualizar['nome'] = nome
        if data.get('email'):
            email = data['email'].strip().lower()
            if not validar_email(email):
                return jsonify({
                    "success": False, 
                    "message": "Email inválido"
                }), 400
            hemocentro_email = HemocentroModel.buscar_por_email(email)
            if hemocentro_email and hemocentro_email['cnpj'] != cnpj_limpo:
                return jsonify({
                    "success": False,
                    "message": "Email já cadastrado em outro hemocentro"
                }), 400
            campos_para_atualizar['email'] = email
        if data.get('telefone'):
            telefone = only_numbers(data['telefone'])
            if not validar_telefone(telefone):
                return jsonify({
                    "success": False, 
                    "message": "Telefone inválido. Use formato: (XX) XXXXX-XXXX"
                }), 400
            campos_para_atualizar['telefone'] = telefone
        if data.get('endereco'):
            endereco = data['endereco'].strip()
            if len(endereco) > 300:
                return jsonify({
                    "success": False, 
                    "message": "Endereço muito longo (máximo 300 caracteres)"
                }), 400
            campos_para_atualizar['endereco'] = endereco
        if data.get('cidade'):
            cidade = data['cidade'].strip()
            if len(cidade) > 100:
                return jsonify({
                    "success": False, 
                    "message": "Nome da cidade muito longo (máximo 100 caracteres)"
                }), 400
            campos_para_atualizar['cidade'] = cidade
        if data.get('estado'):
            estado = data['estado'].strip().upper()
            if not validar_estado(estado):
                return jsonify({
                    "success": False, 
                    "message": "Estado inválido. Apenas SP é aceito no MVP"
                }), 400
            campos_para_atualizar['estado'] = estado
        if data.get('cep'):
            cep = only_numbers(data['cep'])
            if not validar_cep(cep):
                return jsonify({
                    "success": False, 
                    "message": "CEP inválido. Deve ter 8 dígitos"
                }), 400
            campos_para_atualizar['cep'] = cep
        if 'site' in data:
            site = data['site'].strip() if data['site'] else None
            if site:
                if len(site) > 200:
                    return jsonify({
                        "success": False, 
                        "message": "URL do site muito longa (máximo 200 caracteres)"
                    }), 400
                if not site.startswith(('http://', 'https://')):
                    site = f"https://{site}"
            campos_para_atualizar['site'] = site
        if not campos_para_atualizar:
            return jsonify({
                "success": False,
                "message": "Nenhum campo válido para atualizar"
            }), 400
        sucesso = HemocentroModel.atualizar(cnpj_limpo, campos_para_atualizar)
        if not sucesso:
            return jsonify({
                "success": False,
                "message": "Erro ao atualizar hemocentro"
            }), 500
        hemocentro_atualizado = HemocentroModel.buscar_por_cnpj(cnpj_limpo)
        
        return jsonify({
            "success": True,
            "message": "Hemocentro atualizado com sucesso",
            "hemocentro": hemocentro_atualizado
        }), 200
        
    except ValueError as ve:
        return jsonify({
            "success": False,
            "message": str(ve)
        }), 400
    except Exception as e:
        print(f"[ERRO] Atualizar hemocentro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao atualizar hemocentro"
        }), 500

# desativar hemocentro
@hemocentro_bp.route('/hemocentros/<cnpj>', methods=['DELETE'])
@requer_colaborador
def desativar_hemocentro(current_user, cnpj):
    try:
        if not is_cnpj(cnpj):
            return jsonify({
                "success": False,
                "message": "CNPJ inválido"
            }), 400
        cnpj_limpo = only_numbers(cnpj)
        cnpj_colaborador = g.hemocentro.get('cnpj')
        if cnpj_limpo != cnpj_colaborador:
            return jsonify({
                "success": False,
                "message": "Você só pode desativar o seu próprio hemocentro"
            }), 403
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj_limpo)
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        if not hemocentro.get('ativo', False):
            return jsonify({
                "success": False,
                "message": "Hemocentro já está desativado"
            }), 400
        sucesso = HemocentroModel.desativar(cnpj_limpo)
        if not sucesso:
            return jsonify({
                "success": False,
                "message": "Erro ao desativar hemocentro"
            }), 500
        return jsonify({
            "success": True,
            "message": "Hemocentro desativado com sucesso"
        }), 200
        
    except ValueError as ve:
        return jsonify({
            "success": False,
            "message": str(ve)
        }), 400
    except Exception as e:
        print(f"[ERRO] Desativar hemocentro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao desativar hemocentro"
        }), 500


# reativar hemocentro
@hemocentro_bp.route('/hemocentros/<cnpj>/reativar', methods=['PATCH'])
@requer_colaborador
def reativar_hemocentro(current_user, cnpj):
    try:
        if not is_cnpj(cnpj):
            return jsonify({
                "success": False,
                "message": "CNPJ inválido"
            }), 400
        cnpj_limpo = only_numbers(cnpj)
        cnpj_colaborador = g.hemocentro.get('cnpj')
        if cnpj_limpo != cnpj_colaborador:
            return jsonify({
                "success": False,
                "message": "Você só pode reativar o seu próprio hemocentro"
            }), 403
        hemocentro = HemocentroModel.buscar_por_cnpj(cnpj_limpo)
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        if hemocentro.get('ativo', False):
            return jsonify({
                "success": False,
                "message": "Hemocentro já está ativo"
            }), 400
        sucesso = HemocentroModel.reativar(cnpj_limpo)
        if not sucesso:
            return jsonify({
                "success": False,
                "message": "Erro ao reativar hemocentro"
            }), 500
        return jsonify({
            "success": True,
            "message": "Hemocentro reativado com sucesso"
        }), 200
        
    except ValueError as ve:
        return jsonify({
            "success": False,
            "message": str(ve)
        }), 400
    except Exception as e:
        print(f"[ERRO] Reativar hemocentro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao reativar hemocentro"
        }), 500

# buscar hemocentro colaborador
@hemocentro_bp.route('/meu-hemocentro', methods=['GET'])
@requer_colaborador
def buscar_meu_hemocentro(current_user):
    try:
        return jsonify({
            "success": True,
            "hemocentro": g.hemocentro
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Buscar meu hemocentro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao buscar hemocentro"
        }), 500