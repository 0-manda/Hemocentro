from flask import Blueprint, request, jsonify, g
from back.models import EstoqueModel, HemocentroModel
from back.utils.auth_utils import requer_colaborador, validar_tipo_sanguineo

estoque_bp = Blueprint('estoque_bp', __name__)
def obter_hemocentro_sistema():
    hemocentros = HemocentroModel.listar_ativos()
    return hemocentros[0] if hemocentros else None

# adcionar no estoque
@estoque_bp.route('/estoque/adicionar', methods=['POST'])
@requer_colaborador
def adicionar_estoque(current_user):
    try:
        data = request.json or {}
        campos_obrigatorios = ['tipo_sanguineo', 'quantidade']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        tipo_sanguineo = data['tipo_sanguineo'].strip().upper()
        if not validar_tipo_sanguineo(tipo_sanguineo):
            return jsonify({
                "success": False, 
                "message": "Tipo sanguíneo inválido. Use: A+, A-, B+, B-, AB+, AB-, O+, O-"
            }), 400
        try:
            quantidade = int(data['quantidade'])
            if quantidade <= 0:
                return jsonify({
                    "success": False, 
                    "message": "Quantidade deve ser maior que zero"
                }), 400
            if quantidade > 1000:
                return jsonify({
                    "success": False, 
                    "message": "Quantidade muito alta. Máximo 1000 unidades por operação"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False, 
                "message": "Quantidade deve ser um número inteiro"
            }), 400
        estoque_atualizado = EstoqueModel.adicionar_estoque(
            id_hemocentro=g.id_hemocentro,
            tipo_sanguineo=tipo_sanguineo,
            quantidade=quantidade
        )
        return jsonify({
            "success": True,
            "message": f"{quantidade} unidade(s) de {tipo_sanguineo} adicionada(s) ao estoque",
            "estoque": estoque_atualizado
        }), 200 
    except Exception as e:
        print(f"[ERRO] Adicionar estoque: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "message": "Erro ao adicionar ao estoque"
        }), 500

# remover do estoque
@estoque_bp.route('/estoque/remover', methods=['POST'])
@requer_colaborador
def remover_estoque(current_user):
    try:
        data = request.json or {}
        campos_obrigatorios = ['tipo_sanguineo', 'quantidade']
        for campo in campos_obrigatorios:
            if not data.get(campo):
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        tipo_sanguineo = data['tipo_sanguineo'].strip().upper()
        if not validar_tipo_sanguineo(tipo_sanguineo):
            return jsonify({
                "success": False, 
                "message": "Tipo sanguíneo inválido"
            }), 400
        try:
            quantidade = int(data['quantidade'])
            if quantidade <= 0:
                return jsonify({
                    "success": False, 
                    "message": "Quantidade deve ser maior que zero"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False, 
                "message": "Quantidade deve ser um número inteiro"
            }), 400
        estoque_atual = EstoqueModel.buscar_estoque(
            id_hemocentro=g.id_hemocentro,
            tipo_sanguineo=tipo_sanguineo
        )
        if not estoque_atual:
            return jsonify({
                "success": False,
                "message": f"Nenhum estoque de {tipo_sanguineo} encontrado"
            }), 404
        quantidade_disponivel = estoque_atual.get('quantidade', 0)
        if quantidade_disponivel < quantidade:
            return jsonify({
                "success": False,
                "message": f"Estoque insuficiente. Disponível: {quantidade_disponivel} unidade(s)"
            }), 400
        estoque_atualizado = EstoqueModel.remover_estoque(
            id_hemocentro=g.id_hemocentro,
            tipo_sanguineo=tipo_sanguineo,
            quantidade=quantidade
        )
        return jsonify({
            "success": True,
            "message": f"{quantidade} unidade(s) de {tipo_sanguineo} removida(s) do estoque",
            "estoque": estoque_atualizado
        }), 200
    except Exception as e:
        print(f"[ERRO] Remover estoque: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False, 
            "message": "Erro ao remover do estoque"
        }), 500

# publico consultar estoque
@estoque_bp.route('/estoque', methods=['GET'])
def consultar_estoque():
    try:
        hemocentro = obter_hemocentro_sistema()
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        estoque = EstoqueModel.listar_estoque_hemocentro(hemocentro['id_hemocentro'])
        total_unidades = sum(item.get('quantidade', 0) for item in estoque)
        tipos_criticos = sum(1 for item in estoque if item.get('nivel') == 'critico')
        return jsonify({
            "success": True,
            "hemocentro": {
                "id_hemocentro": hemocentro['id_hemocentro'],
                "nome": hemocentro['nome'],
                "endereco": hemocentro.get('endereco'),
                "cidade": hemocentro.get('cidade'),
                "telefone": hemocentro.get('telefone')
            },
            "estoque": estoque,
            "resumo": {
                "total_unidades": total_unidades,
                "tipos_disponiveis": len(estoque),
                "tipos_criticos": tipos_criticos
            }
        }), 200
    except Exception as e:
        print(f"[ERRO] Consultar estoque: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao consultar estoque"
        }), 500

# cuonsulta de tipo sanguineo específico
# @estoque_bp.route('/estoque/<tipo_sanguineo>', methods=['GET'])
# def consultar_tipo_especifico(tipo_sanguineo):
#     try:
#         tipo_sanguineo = tipo_sanguineo.strip().upper()
#         if not validar_tipo_sanguineo(tipo_sanguineo):
#             return jsonify({
#                 "success": False,
#                 "message": "Tipo sanguíneo inválido"
#             }), 400
#         hemocentro = obter_hemocentro_sistema()
#         if not hemocentro:
#             return jsonify({
#                 "success": False,
#                 "message": "Hemocentro não encontrado"
#             }), 404
#         estoque = EstoqueModel.buscar_estoque(
#             id_hemocentro=hemocentro['id_hemocentro'],
#             tipo_sanguineo=tipo_sanguineo
#         )
#         if not estoque:
#             return jsonify({
#                 "success": True,
#                 "tipo_sanguineo": tipo_sanguineo,
#                 "quantidade": 0,
#                 "nivel": "critico",
#                 "necessita_doacao": True
#             }), 200
#         return jsonify({
#             "success": True,
#             "estoque": estoque
#         }), 200     
#     except Exception as e:
#         print(f"[ERRO] Consultar tipo específico: {str(e)}")
#         import traceback
#         traceback.print_exc()
#         return jsonify({
#             "success": False,
#             "message": "Erro ao consultar estoque"
#         }), 500

# listar estoques críticos
@estoque_bp.route('/estoque/criticos', methods=['GET'])
def listar_estoques_criticos():
    try:
        limite_critico = request.args.get('limite', 10, type=int)
        if limite_critico < 0:
            return jsonify({
                "success": False,
                "message": "Limite deve ser maior ou igual a zero"
            }), 400
        estoques_criticos = EstoqueModel.listar_estoques_criticos(limite_critico)
        return jsonify({
            "success": True,
            "total": len(estoques_criticos),
            "limite_critico": limite_critico,
            "estoques": estoques_criticos,
            "alerta": len(estoques_criticos) > 0
        }), 200
    except Exception as e:
        print(f"[ERRO] Listar estoques críticos: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao listar estoques críticos"
        }), 500

# atualizar estoque diretamente
@estoque_bp.route('/estoque/atualizar', methods=['PUT'])
@requer_colaborador
def atualizar_estoque_direto(current_user):
    try:
        data = request.json or {}
        campos_obrigatorios = ['tipo_sanguineo', 'quantidade']
        for campo in campos_obrigatorios:
            if campo not in data:
                return jsonify({
                    "success": False,
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        tipo_sanguineo = data['tipo_sanguineo'].strip().upper()
        if not validar_tipo_sanguineo(tipo_sanguineo):
            return jsonify({
                "success": False,
                "message": "Tipo sanguíneo inválido"
            }), 400
        try:
            quantidade = int(data['quantidade'])
            if quantidade < 0:
                return jsonify({
                    "success": False,
                    "message": "Quantidade não pode ser negativa"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Quantidade deve ser um número inteiro"
            }), 400
        estoque_atualizado = EstoqueModel.atualizar_quantidade(
            id_hemocentro=g.id_hemocentro,
            tipo_sanguineo=tipo_sanguineo,
            quantidade=quantidade
        )
        return jsonify({
            "success": True,
            "message": f"Estoque de {tipo_sanguineo} atualizado para {quantidade} unidade(s)",
            "estoque": estoque_atualizado
        }), 200
    except Exception as e:
        print(f"[ERRO] Atualizar estoque direto: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao atualizar estoque"
        }), 500
    
#consultar estoque por hemocentro específico
@estoque_bp.route('/estoque/hemocentro/<int:id_hemocentro>', methods=['GET'])
def consultar_estoque_por_hemocentro(id_hemocentro):
    try:
        hemocentro = HemocentroModel.buscar_por_id(id_hemocentro)
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        if not hemocentro.get('ativo'):
            return jsonify({
                "success": False,
                "message": "Hemocentro inativo"
            }), 404
        estoque = EstoqueModel.listar_estoque_hemocentro(id_hemocentro)
        total_unidades = sum(item.get('quantidade', 0) for item in estoque)
        tipos_criticos = sum(1 for item in estoque if item.get('nivel') == 'critico')
        return jsonify({
            "success": True,
            "hemocentro": {
                "id_hemocentro": hemocentro['id_hemocentro'],
                "nome": hemocentro['nome'],
                "endereco": hemocentro.get('endereco'),
                "cidade": hemocentro.get('cidade'),
                "telefone": hemocentro.get('telefone')
            },
            "estoque": estoque,
            "resumo": {
                "total_unidades": total_unidades,
                "tipos_disponiveis": len(estoque),
                "tipos_criticos": tipos_criticos
            }
        }), 200
    except Exception as e:
        print(f"[ERRO] Consultar estoque por hemocentro: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao consultar estoque"
        }), 500