from flask import Blueprint, request, jsonify
from utils.auth_utils import hemocentro_required, admin_required, validar_email, validar_telefone, only_numbers, is_cnpj
from models.models import HemocentroModel
from datetime import datetime

hemocentro_bp = Blueprint('hemocentro_bp', __name__)

@hemocentro_bp.route('/hemocentro', methods=['POST'])
@admin_required
def cadastrar_hemocentro():
    try:
        data = request.json or {}
        campos_necessarios = ['nome', 'email', 'cnpj','telefone', 'endereco', 'cidade', 'estado', 'cep', 'site', 'data_cadastro', 'ativo']
        for campo in campos_necessarios:
            if campo not in data or not data.get(campo):
                return jsonify({"success": False, "message": f"Campo obrigatório faltando: {campo}"}), 400
        
        nome=data['nome'].strip()
        email=data['email'].strip().lower()
        cnpj=only_numbers(data['cnpj'])
        telefone=only_numbers(data['telefone'])
        endereco=data['endereco'].strip()
        cidade=data['cidade'].strip()
        estado=data['estado'].strip().upper()
        cep=only_numbers(data['cep'])
        site=data.get('site', '').strip()
        data_cadastro=datetime.now()
        ativo=data['ativo']

        if not is_cnpj(cnpj):
            return jsonify({"success": False, "message": "CNPJ inválido."}), 400
        if HemocentroModel.buscar_por_cnpj(cnpj):
            return jsonify({"success": False, "message": "CNPJ já cadastrado."}), 400
        if not validar_email(email):
            return jsonify({"success": False, "message": "Email inválido."}), 400
        if not validar_telefone(telefone):
            return jsonify({"success": False, "message": "Telefone inválido."}), 400
        if len (cep) != 8:
            return jsonify({"success": False, "message": "CEP inválido."}), 400
        estados_validos = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
        if estado not in estados_validos:
            return jsonify({"success": False, "message": "Estado inválido."}), 400
        
        hemocentro = HemocentroModel.criar_hemocentro(
            nome=nome,
            email=email,
            cnpj=cnpj,
            telefone=telefone,
            endereco=endereco,
            cidade=cidade,
            estado=estado,
            cep=cep,
            site=site if site else None,
            data_cadastro=datetime.now(),
            ativo=True
        )
        return jsonify({"success": True, "message": "hemocentro cadastrado com sucesso.","hemocentro":hemocentro}), 201
    except ValueError as e:
        print("Erro ao cadastrar hemocentro:", str(e))
        return jsonify({"success": False,"message": f"Erro de validação: {str(e)}"}), 400

        return jsonify({"success": False, "message": "Erro interno."}), 500
@hemocentro_bp.route('/hemocentros', methods=['GET'])
def listar_hemocentros():
    """
    NOVO: Lista hemocentros ativos
    MOTIVO: Doadores precisam ver hemocentros disponíveis
    
    Filtros opcionais:
      - ?cidade=Campinas
      - ?estado=SP
    """
    try:
        cidade = request.args.get('cidade')
        estado = request.args.get('estado')
        
        hemocentros = HemocentroModel.listar_ativos(cidade=cidade, estado=estado)
        
        return jsonify({
            "success": True,
            "hemocentros": hemocentros,
            "total": len(hemocentros)
        }), 200
        
    except Exception as e:
        print(f"Erro ao listar hemocentros: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== BUSCAR HEMOCENTRO POR ID (PÚBLICO) =====

@hemocentro_bp.route('/hemocentros/<int:hemocentro_id>', methods=['GET'])
def buscar_hemocentro(hemocentro_id):
    """
    NOVO: Busca detalhes de um hemocentro
    MOTIVO: Página de detalhes do hemocentro
    """
    try:
        hemocentro = HemocentroModel.buscar_por_id(hemocentro_id)
        
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado."
            }), 404
        
        # Busca também horários de funcionamento
        # horarios = HorarioFuncionamentoModel.listar_por_hemocentro(hemocentro_id)
        # hemocentro['horarios'] = horarios
        
        return jsonify({
            "success": True,
            "hemocentro": hemocentro
        }), 200
        
    except Exception as e:
        print(f"Erro ao buscar hemocentro: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500


# ===== ATUALIZAR HEMOCENTRO =====

@hemocentro_bp.route('/hemocentros/<int:hemocentro_id>', methods=['PUT'])
@admin_required  # Só admin atualiza (ou pode mudar para hemocentro_required)
def atualizar_hemocentro(current_user, hemocentro_id):
    """
    NOVO: Atualiza dados do hemocentro
    MOTIVO: Editar informações
    
    DECISÃO: Você escolhe quem pode editar:
      - @admin_required → Só admin
      - @hemocentro_required → O próprio hemocentro
    """
    try:
        data = request.json or {}
        
        # Busca hemocentro
        hemocentro = HemocentroModel.buscar_por_id(hemocentro_id)
        
        if not hemocentro:
            return jsonify({
                "success": False,
                "message": "Hemocentro não encontrado."
            }), 404
        
        # Campos editáveis
        campos_editaveis = {
            'nome': data.get('nome'),
            'email': data.get('email'),
            'telefone': data.get('telefone'),
            'endereco': data.get('endereco'),
            'cidade': data.get('cidade'),
            'estado': data.get('estado'),
            'cep': data.get('cep'),
            'site': data.get('site'),
            'ativo': data.get('ativo')
        }
        
        # Remove campos None
        campos_para_atualizar = {k: v for k, v in campos_editaveis.items() if v is not None}
        
        if not campos_para_atualizar:
            return jsonify({
                "success": False,
                "message": "Nenhum campo para atualizar."
            }), 400
        
        # Validações (simplificadas)
        if 'email' in campos_para_atualizar and not validar_email(campos_para_atualizar['email']):
            return jsonify({"success": False, "message": "Email inválido."}), 400
        
        if 'telefone' in campos_para_atualizar:
            tel = only_numbers(campos_para_atualizar['telefone'])
            if not validar_telefone(tel):
                return jsonify({"success": False, "message": "Telefone inválido."}), 400
            campos_para_atualizar['telefone'] = tel
        
        # Atualiza
        HemocentroModel.atualizar(hemocentro_id, campos_para_atualizar)
        
        return jsonify({
            "success": True,
            "message": "Hemocentro atualizado com sucesso!"
        }), 200
        
    except Exception as e:
        print(f"Erro ao atualizar hemocentro: {str(e)}")
        return jsonify({
            "success": False,
            "message": "Erro interno do servidor."
        }), 500

    