from flask import Blueprint, request, jsonify, g
from back.models import CampanhaModel, HemocentroModel
from back.utils.auth_utils import requer_colaborador
from datetime import datetime

campanha_bp = Blueprint('campanha_bp', __name__)

# criar campanha
@campanha_bp.route('/cadastrar_campanha', methods=['POST'])
@requer_colaborador
def criar_campanha(current_user):
    try:
        data = request.json or {}
        campos_necessarios = [
            'nome', 'descricao', 'data_inicio', 'data_fim', 
            'tipo_sanguineo_necessario', 'quantidade_meta_litros', 'objetivo'
        ]
        for campo in campos_necessarios:
            if campo not in data or not data.get(campo):
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        if len(data['nome'].strip()) > 200:
            return jsonify({
                "success": False, 
                "message": "Nome muito longo (máximo 200 caracteres)"
            }), 400
        if len(data['descricao'].strip()) > 1000:
            return jsonify({
                "success": False, 
                "message": "Descrição muito longa (máximo 1000 caracteres)"
            }), 400
        if len(data['objetivo'].strip()) > 500:
            return jsonify({
                "success": False, 
                "message": "Objetivo muito longo (máximo 500 caracteres)"
            }), 400
        tipos_validos = ['Todos','A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        tipo_sanguineo = data['tipo_sanguineo_necessario'].strip().upper()
        if tipo_sanguineo not in tipos_validos:
            return jsonify({
                "success": False, 
                "message": f"Tipo sanguíneo inválido. Use: {', '.join(tipos_validos)}"
            }), 400
        try:
            data_inicio = datetime.strptime(data['data_inicio'], '%Y-%m-%d')
            data_fim = datetime.strptime(data['data_fim'], '%Y-%m-%d')
            if data_fim <= data_inicio:
                return jsonify({
                    "success": False, 
                    "message": "Data de fim deve ser posterior à data de início."
                }), 400
            if data_inicio < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                return jsonify({
                    "success": False, 
                    "message": "Data de início não pode ser no passado."
                }), 400       
        except ValueError:
            return jsonify({
                "success": False, 
                "message": "Formato de data inválido. Use 'YYYY-MM-DD'."
            }), 400
        try:
            quantidade_meta_litros = int(data['quantidade_meta_litros'])
            if quantidade_meta_litros <= 0:
                raise ValueError
        except (ValueError, TypeError):
            return jsonify({
                "success": False, 
                "message": "Quantidade meta deve ser um número inteiro positivo."
            }), 400
        
        campanha = CampanhaModel.criar(
            id_hemocentro=g.id_hemocentro,
            nome=data['nome'].strip(),
            descricao=data['descricao'].strip(),
            data_inicio=data['data_inicio'],
            data_fim=data['data_fim'],
            tipo_sanguineo_necessario=tipo_sanguineo,
            quantidade_meta_litros=quantidade_meta_litros,
            objetivo=data['objetivo'].strip(),
            ativa=True,
            destaque=data.get('destaque', False)
        )
        return jsonify({
            "success": True,
            "message": "Campanha criada com sucesso!",
            "campanha": campanha
        }), 201
        
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": f"Erro de validação: {str(e)}"
        }), 400
    except Exception as e:
        print(f"[ERRO] Criar campanha: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500

# campanhas ativas
@campanha_bp.route('/campanhas', methods=['GET'])
def listar_campanhas():
    try:
        id_hemocentro = request.args.get('id_hemocentro', type=int)
        tipo_sanguineo = request.args.get('tipo_sanguineo')
        apenas_destaque = request.args.get('destaque', 'false').lower() == 'true'
        if tipo_sanguineo:
            tipos_validos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            tipo_sanguineo = tipo_sanguineo.strip().upper()
            if tipo_sanguineo not in tipos_validos:
                return jsonify({
                    "success": False,
                    "message": f"Tipo sanguíneo inválido. Use: {', '.join(tipos_validos)}"
                }), 400
        campanhas = CampanhaModel.listar_ativas(
            id_hemocentro=id_hemocentro,
            tipo_sanguineo_necessario=tipo_sanguineo,
            apenas_destaque=apenas_destaque
        )
        return jsonify({
            "success": True,
            "campanhas": campanhas,
            "total": len(campanhas)
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Listar campanhas: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500

# buscar campanha por id
# @campanha_bp.route('/campanhas/<int:campanha_id>', methods=['GET'])
# def buscar_campanha(campanha_id):
#     try:
#         campanha = CampanhaModel.buscar_por_id(campanha_id)
        
#         if not campanha:
#             return jsonify({
#                 "success": False,
#                 "message": "Campanha não encontrada."
#             }), 404
#         return jsonify({
#             "success": True,
#             "campanha": campanha
#         }), 200
        
#     except Exception as e:
#         print(f"[ERRO] Buscar campanha: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False,
#             "message": "Erro interno do servidor."
#         }), 500


# atualizar campanha
@campanha_bp.route('/campanhas/<int:campanha_id>', methods=['PUT'])
@requer_colaborador
def atualizar_campanha(current_user, campanha_id):
    try:
        data = request.json or {}
        campanha = CampanhaModel.buscar_por_id(campanha_id)
        if not campanha:
            return jsonify({
                "success": False,
                "message": "Campanha não encontrada."
            }), 404
        if campanha['id_hemocentro'] != g.id_hemocentro:
            return jsonify({
                "success": False,
                "message": "Você só pode editar campanhas do seu hemocentro."
            }), 403
        campos_editaveis = {
            'nome': data.get('nome'),
            'descricao': data.get('descricao'),
            'data_fim': data.get('data_fim'),
            'tipo_sanguineo_necessario': data.get('tipo_sanguineo_necessario'),
            'quantidade_meta_litros': data.get('quantidade_meta_litros'),
            'quantidade_atual_litros': data.get('quantidade_atual_litros'),
            'objetivo': data.get('objetivo'),
            'ativa': data.get('ativa'),
            'destaque': data.get('destaque')
        }
        campos_para_atualizar = {k: v for k, v in campos_editaveis.items() if v is not None}
        if not campos_para_atualizar:
            return jsonify({
                "success": False,
                "message": "Nenhum campo para atualizar."
            }), 400
        if 'nome' in campos_para_atualizar and len(campos_para_atualizar['nome'].strip()) > 200:
            return jsonify({
                "success": False,
                "message": "Nome muito longo (máximo 200 caracteres)"
            }), 400
        if 'descricao' in campos_para_atualizar and len(campos_para_atualizar['descricao'].strip()) > 1000:
            return jsonify({
                "success": False,
                "message": "Descrição muito longa (máximo 1000 caracteres)"
            }), 400
        if 'objetivo' in campos_para_atualizar and len(campos_para_atualizar['objetivo'].strip()) > 500:
            return jsonify({
                "success": False,
                "message": "Objetivo muito longo (máximo 500 caracteres)"
            }), 400
        if 'tipo_sanguineo_necessario' in campos_para_atualizar:
            tipos_validos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
            tipo = campos_para_atualizar['tipo_sanguineo_necessario'].strip().upper()
            if tipo not in tipos_validos:
                return jsonify({
                    "success": False,
                    "message": f"Tipo sanguíneo inválido. Use: {', '.join(tipos_validos)}"
                }), 400
            campos_para_atualizar['tipo_sanguineo_necessario'] = tipo
        if 'data_fim' in campos_para_atualizar:
            try:
                data_fim = datetime.strptime(campos_para_atualizar['data_fim'], '%Y-%m-%d')
                data_inicio = datetime.strptime(campanha['data_inicio'], '%Y-%m-%d')
                
                if data_fim <= data_inicio:
                    return jsonify({
                        "success": False,
                        "message": "Data de término deve ser posterior à data de início."
                    }), 400
            except ValueError:
                return jsonify({
                    "success": False,
                    "message": "Formato de data inválido. Use: YYYY-MM-DD"
                }), 400
        if 'quantidade_meta_litros' in campos_para_atualizar:
            try:
                quantidade = int(campos_para_atualizar['quantidade_meta_litros'])
                if quantidade <= 0:
                    raise ValueError
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "message": "Quantidade meta deve ser um número inteiro positivo."
                }), 400
        if 'quantidade_atual_litros' in campos_para_atualizar:
            try:
                quantidade = int(campos_para_atualizar['quantidade_atual_litros'])
                if quantidade < 0:
                    raise ValueError
            except (ValueError, TypeError):
                return jsonify({
                    "success": False,
                    "message": "Quantidade atual deve ser um número inteiro não-negativo."
                }), 400
        CampanhaModel.atualizar(campanha_id, campos_para_atualizar)
        
        return jsonify({
            "success": True,
            "message": "Campanha atualizada com sucesso!"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Atualizar campanha: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500

# desativar campanha
@campanha_bp.route('/campanhas/<int:campanha_id>', methods=['DELETE'])
@requer_colaborador
def desativar_campanha(current_user, campanha_id):
    try:
        campanha = CampanhaModel.buscar_por_id(campanha_id)  
        if not campanha:
            return jsonify({
                "success": False,
                "message": "Campanha não encontrada."
            }), 404
        if campanha['id_hemocentro'] != g.id_hemocentro:
            return jsonify({
                "success": False,
                "message": "Você só pode desativar campanhas do seu hemocentro."
            }), 403
        CampanhaModel.desativar(campanha_id)
        return jsonify({
            "success": True,
            "message": "Campanha desativada com sucesso!"
        }), 200
        
    except Exception as e:
        print(f"[ERRO] Desativar campanha: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500

# listar minhas campanhas (colaborador)
# @campanha_bp.route('/minhas-campanhas', methods=['GET'])
# @requer_colaborador
# def minhas_campanhas(current_user):
#     try:
#         campanhas = CampanhaModel.listar_por_hemocentro(g.id_hemocentro)
#         return jsonify({
#             "success": True,
#             "campanhas": campanhas,
#             "total": len(campanhas)
#         }), 200
        
#     except Exception as e:
#         print(f"[ERRO] Listar minhas campanhas: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False,
#             "message": "Erro interno do servidor."
#         }), 500