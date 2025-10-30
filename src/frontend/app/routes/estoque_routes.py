from flask import Blueprint, request, jsonify
from models.models import EstoqueModel, HemocentroModel
from utils.auth_utils import hemocentro_required, validar_tipo_sanguineo, token_required

estoque_bp = Blueprint('estoque_bp', __name__)

@estoque_bp.route('/acionar_estoque', methods=['POST'])
@token_required
@hemocentro_required
def adcionar_estoque():
    try:
        data = request.json or {}
        campos_necessarios = ['hemocentro_id','tipo_sanguineo', 'quantidade_adicionar']
        for campo in campos_necessarios:
            if campo not in data or not data.get(campo):
                return jsonify({"success": False, "message": f"Campo obrigatório faltando: {campo}" }), 400
        
        hemocentro_id=data['hemocentro_id']
        tipo_sanguineo=data['tipo_sanguineo'].upper()
        quantidade_adicionar=data['quantidade_adicionar']

        try:
            quantidade_adicionar = int(quantidade_adicionar)
            if quantidade_adicionar <= 0:
                return jsonify({"success": False, "message": "Quantidade deve ser maior que zero"}), 400
        except(ValueError, TypeError):
            return jsonify({"success": False, "message": "Quantidade inválida"}), 400
        
        hemocentro = HemocentroModel.buscar_por_id(hemocentro_id)
        if not hemocentro:
            return jsonify({"success": False, "message": "Hemocentro não encontrado."}), 404
        if not hemocentro.get('ativo', False):
            return jsonify({"success": False, "message": "Hemocentro inativo."}), 400
        if not validar_tipo_sanguineo(tipo_sanguineo):
            return jsonify({
                "success": False, 
                "message": "Tipo sanguíneo inválido. Tipos válidos: A+, A-, B+, B-, AB+, AB-, O+, O-"
            }), 400
        
        estoque_atualizado = EstoqueModel.adcionar_estoque(
            hemocentro_id = hemocentro_id,
            tipo_sanguineo = tipo_sanguineo,
            quantidade_adicionar = quantidade_adicionar
        )

        return jsonify ({"success": True,
            "message": "Estoque atualizado com sucesso",
            "estoque": estoque_atualizado
        }), 200
    except Exception as e:
        print(f"Erro ao adicionar estoque: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "Erro ao atualizar estoque"
        }), 500
    
# ============== REMOVER DO ESTOQUE ==============
@estoque_bp.route('/remover_estoque', methods=['POST'])
@token_required
@hemocentro_required
def remover_estoque(current_user):
    """
    Remove quantidade do estoque de sangue
    Usado quando sangue é utilizado ou descartado
    """
    try:
        data = request.json or {}
        
        campos_necessarios = ['hemocentro_id', 'tipo_sanguineo', 'quantidade_remover']
        for campo in campos_necessarios:
            if not data.get(campo):
                return jsonify({
                    "success": False, 
                    "message": f"Campo obrigatório faltando: {campo}"
                }), 400
        
        hemocentro_id = data['hemocentro_id']
        tipo_sanguineo = data['tipo_sanguineo'].upper()
        quantidade_remover = data['quantidade_remover']
        motivo = data.get('motivo', 'uso')  # 'uso', 'descarte', 'vencimento'
        
        # Validação: Quantidade positiva
        try:
            quantidade_remover = int(quantidade_remover)
            if quantidade_remover <= 0:
                return jsonify({
                    "success": False, 
                    "message": "Quantidade deve ser maior que zero"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False, 
                "message": "Quantidade inválida"
            }), 400
        
        # Validação: Hemocentro existe e está ativo
        hemocentro = HemocentroModel.buscar_por_id(hemocentro_id)
        if not hemocentro or not hemocentro.get('ativo', False):
            return jsonify({
                "success": False, 
                "message": "Hemocentro não encontrado ou inativo"
            }), 404
        
        # Validação: Tipo sanguíneo válido
        if not validar_tipo_sanguineo(tipo_sanguineo):
            return jsonify({
                "success": False, 
                "message": "Tipo sanguíneo inválido"
            }), 400
        
        # Verificar se há estoque suficiente
        estoque_atual = EstoqueModel.buscar_estoque(hemocentro_id, tipo_sanguineo)
        if not estoque_atual or estoque_atual['quantidade'] < quantidade_remover:
            return jsonify({
                "success": False,
                "message": f"Estoque insuficiente. Disponível: {estoque_atual['quantidade'] if estoque_atual else 0} unidades"
            }), 400
        
        # Remover do estoque
        estoque_atualizado = EstoqueModel.remover_estoque(
            hemocentro_id=hemocentro_id,
            tipo_sanguineo=tipo_sanguineo,
            quantidade=quantidade_remover,
            motivo=motivo
        )
        
        return jsonify({
            "success": True,
            "message": "Estoque atualizado com sucesso",
            "estoque": estoque_atualizado
        }), 200
        
    except Exception as e:
        print(f"Erro ao remover estoque: {str(e)}")
        return jsonify({
            "success": False, 
            "message": "Erro ao atualizar estoque"
        }), 500


@estoque_bp.route('/estoque/<int:hemocentro_id>', methods=['GET'])
def consultar_estoque(hemocentro_id):
    try:
        # Verificar se hemocentro existe
        hemocentro = HemocentroModel.buscar_por_id(hemocentro_id)
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado"
            }), 404
        
        # Buscar estoque completo
        estoque = EstoqueModel.listar_estoque_hemocentro(hemocentro_id)
        
        return jsonify({
            "success": True,
            "hemocentro": {
                "id": hemocentro['id'],
                "nome": hemocentro['nome'],
                "endereco": hemocentro.get('endereco')
            },
            "estoque": estoque
        }), 200
        
    except Exception as e:
        print(f"Erro ao consultar estoque: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao consultar estoque"
        }), 500

# ============== LISTAR ESTOQUES CRÍTICOS ==============
@estoque_bp.route('/estoques_criticos', methods=['GET'])
def listar_estoques_criticos():
    """
    Lista todos os tipos sanguíneos com estoque crítico
    Útil para alertas e campanhas
    """
    try:
        # Parâmetro opcional: limite crítico (padrão: 10 unidades)
        limite_critico = request.args.get('limite', 10, type=int)
        
        estoques_criticos = EstoqueModel.listar_estoques_criticos(limite_critico)
        
        return jsonify({
            "success": True,
            "total": len(estoques_criticos),
            "limite_critico": limite_critico,
            "estoques": estoques_criticos
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar estoques críticos: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro ao listar estoques críticos"
        }), 500