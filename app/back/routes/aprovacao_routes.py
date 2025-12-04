from flask import Blueprint, request, jsonify, render_template_string
from back.models import UsuarioModel, HemocentroModel
from back.models.aprovacao_model import AprovacaoModel
from back.utils.email_utils import enviar_notificacao_aprovacao, enviar_notificacao_rejeicao

aprovacao_bp = Blueprint('aprovacao_bp', __name__)

#HTML para página de confirmação
TEMPLATE_CONFIRMACAO = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ titulo }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            padding: 50px;
            max-width: 600px;
            text-align: center;
        }
        .icon {
            font-size: 80px;
            margin-bottom: 20px;
        }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        h1 {
            color: #333;
            margin-bottom: 15px;
            font-size: 28px;
        }
        p {
            color: #666;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 10px;
        }
        .info-box {
            background: #f8f9fa;
            border-left: 4px solid {{ cor }};
            padding: 20px;
            margin: 30px 0;
            text-align: left;
        }
        .info-item {
            margin: 10px 0;
        }
        .label {
            font-weight: bold;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon {{ classe }}"></div>
        <h1>{{ titulo }}</h1>
        <p>{{ mensagem }}</p>
        {% if detalhes %}
        <div class="info-box">
            {% for chave, valor in detalhes.items() %}
            <div class="info-item">
                <span class="label">{{ chave }}:</span> {{ valor }}
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

#endpoint para aprovar um cadastro através do token enviado por email
@aprovacao_bp.route('/aprovar/<token>', methods=['GET'])
def aprovar_cadastro(token):
    try:
        # Validar token
        token_info = AprovacaoModel.validar_token(token)
        
        if not token_info:
            return render_template_string(
                TEMPLATE_CONFIRMACAO,
                titulo="Token Inválido",
                mensagem="Este link de aprovação é inválido ou já foi utilizado.",
                classe="error",
                cor="#dc3545",
                detalhes=None
            ), 400
        
        tipo = token_info['tipo']
        id_entidade = token_info['id_entidade']
        #processar aprovação usuario
        if tipo == 'doador':
            usuario = UsuarioModel.buscar_por_id(id_entidade)
            
            if not usuario:
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Erro",
                    mensagem="Doador não encontrado no sistema.",
                    classe="error",
                    cor="#dc3545",
                    detalhes=None
                ), 404
            
            #ativar o usuário
            sucesso = UsuarioModel.atualizar(id_entidade, {'ativo': True})
            
            if sucesso:
                AprovacaoModel.marcar_como_aprovado(token)
                #enviaer email de notificação
                enviar_notificacao_aprovacao(
                    usuario['email'],
                    usuario['nome'],
                    'doador'
                )
                
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Cadastro Aprovado!",
                    mensagem="O cadastro do doador foi aprovado com sucesso.",
                    classe="success",
                    cor="#28a745",
                    detalhes={
                        "Nome": usuario['nome'],
                        "Email": usuario['email'],
                        "CPF": usuario.get('cpf', 'N/A'),
                        "Tipo Sanguíneo": usuario.get('tipo_sanguineo', 'Não informado'),
                        "Tipo": "Doador"
                    }
                ), 200
            else:
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Erro",
                    mensagem="Erro ao ativar o doador.",
                    classe="error",
                    cor="#dc3545",
                    detalhes=None
                ), 500
        
        #processar aprovação colaborador
        elif tipo == 'colaborador':
            usuario = UsuarioModel.buscar_por_id(id_entidade)
            
            if not usuario:
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Erro",
                    mensagem="Usuário não encontrado no sistema.",
                    classe="error",
                    cor="#dc3545",
                    detalhes=None
                ), 404
            sucesso = UsuarioModel.atualizar(id_entidade, {'ativo': True})
            
            if sucesso:
                AprovacaoModel.marcar_como_aprovado(token)
                enviar_notificacao_aprovacao(
                    usuario['email'],
                    usuario['nome'],
                    'colaborador'
                )
                
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Cadastro Aprovado!",
                    mensagem="O cadastro do colaborador foi aprovado com sucesso.",
                    classe="success",
                    cor="#28a745",
                    detalhes={
                        "Nome": usuario['nome'],
                        "Email": usuario['email'],
                        "Tipo": "Colaborador"
                    }
                ), 200
            else:
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Erro",
                    mensagem="Erro ao ativar o colaborador.",
                    classe="error",
                    cor="#dc3545",
                    detalhes=None
                ), 500
        
        # aprovar hemocentro
        elif tipo == 'hemocentro':
            hemocentro = HemocentroModel.buscar_por_id(id_entidade)
            if not hemocentro:
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Erro",
                    mensagem="Hemocentro não encontrado no sistema.",
                    classe="error",
                    cor="#dc3545",
                    detalhes=None
                ), 404
            sucesso = HemocentroModel.atualizar(
                hemocentro['cnpj'],
                {'ativo': True}
            )
            
            if sucesso:
                AprovacaoModel.marcar_como_aprovado(token)
                enviar_notificacao_aprovacao(
                    hemocentro['email'],
                    hemocentro['nome'],
                    'hemocentro'
                )
                
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Cadastro Aprovado!",
                    mensagem="O cadastro do hemocentro foi aprovado com sucesso.",
                    classe="success",
                    cor="#28a745",
                    detalhes={
                        "Nome": hemocentro['nome'],
                        "Email": hemocentro['email'],
                        "CNPJ": hemocentro['cnpj'],
                        "Tipo": "Hemocentro"
                    }
                ), 200
            else:
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Erro",
                    mensagem="Erro ao ativar o hemocentro.",
                    classe="error",
                    cor="#dc3545",
                    detalhes=None
                ), 500
        
        # tipo inválido
        else:
            return render_template_string(
                TEMPLATE_CONFIRMACAO,
                titulo="Erro",
                mensagem="Tipo de aprovação inválido.",
                classe="error",
                cor="#dc3545",
                detalhes=None
            ), 400
    
    except Exception as e:
        print(f"[ERRO] Aprovar cadastro: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template_string(
            TEMPLATE_CONFIRMACAO,
            titulo="Erro Interno",
            mensagem="Ocorreu um erro ao processar a aprovação. Tente novamente mais tarde.",
            classe="error",
            cor="#dc3545",
            detalhes=None
        ), 500

@aprovacao_bp.route('/rejeitar/<token>', methods=['GET'])
def rejeitar_cadastro(token):
    #endpoint para rejeitar um cadastro através do token enviado por email
    try:
        token_info = AprovacaoModel.validar_token(token)
        if not token_info:
            return render_template_string(
                TEMPLATE_CONFIRMACAO,
                titulo="Token Inválido",
                mensagem="Este link de rejeição é inválido ou já foi utilizado.",
                classe="error",
                cor="#dc3545",
                detalhes=None
            ), 400
        
        tipo = token_info['tipo']
        id_entidade = token_info['id_entidade']
        
        #rejeitar doador
        if tipo == 'doador':
            usuario = UsuarioModel.buscar_por_id(id_entidade)
            
            if not usuario:
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Erro",
                    mensagem="Doador não encontrado no sistema.",
                    classe="error",
                    cor="#dc3545",
                    detalhes=None
                ), 404

            AprovacaoModel.marcar_como_rejeitado(token)
            enviar_notificacao_rejeicao(
                usuario['email'],
                usuario['nome'],
                'doador',
                motivo="Cadastro não aprovado pelo administrador"
            )
            
            return render_template_string(
                TEMPLATE_CONFIRMACAO,
                titulo="Cadastro Rejeitado",
                mensagem="O cadastro do doador foi rejeitado.",
                classe="error",
                cor="#dc3545",
                detalhes={
                    "Nome": usuario['nome'],
                    "Email": usuario['email'],
                    "CPF": usuario.get('cpf', 'N/A'),
                    "Tipo": "Doador"
                }
            ), 200
        
        #rejeitar colaborador
        elif tipo == 'colaborador':
            usuario = UsuarioModel.buscar_por_id(id_entidade)
            
            if not usuario:
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Erro",
                    mensagem="Usuário não encontrado no sistema.",
                    classe="error",
                    cor="#dc3545",
                    detalhes=None
                ), 404
            
            AprovacaoModel.marcar_como_rejeitado(token)
            enviar_notificacao_rejeicao(
                usuario['email'],
                usuario['nome'],
                'colaborador',
                motivo="Cadastro não aprovado pelo administrador"
            )
            
            return render_template_string(
                TEMPLATE_CONFIRMACAO,
                titulo="Cadastro Rejeitado",
                mensagem="O cadastro do colaborador foi rejeitado.",
                classe="error",
                cor="#dc3545",
                detalhes={
                    "Nome": usuario['nome'],
                    "Email": usuario['email'],
                    "Tipo": "Colaborador"
                }
            ), 200
        
        #rejeitar hemocentro
        elif tipo == 'hemocentro':
            hemocentro = HemocentroModel.buscar_por_id(id_entidade)
            
            if not hemocentro:
                return render_template_string(
                    TEMPLATE_CONFIRMACAO,
                    titulo="Erro",
                    mensagem="Hemocentro não encontrado no sistema.",
                    classe="error",
                    cor="#dc3545",
                    detalhes=None
                ), 404
            AprovacaoModel.marcar_como_rejeitado(token)
            enviar_notificacao_rejeicao(
                hemocentro['email'],
                hemocentro['nome'],
                'hemocentro',
                motivo="Cadastro não aprovado pelo administrador"
            )
            
            return render_template_string(
                TEMPLATE_CONFIRMACAO,
                titulo="Cadastro Rejeitado",
                mensagem="O cadastro do hemocentro foi rejeitado.",
                classe="error",
                cor="#dc3545",
                detalhes={
                    "Nome": hemocentro['nome'],
                    "Email": hemocentro['email'],
                    "CNPJ": hemocentro['cnpj'],
                    "Tipo": "Hemocentro"
                }
            ), 200
        
        # tipo inválido
        else:
            return render_template_string(
                TEMPLATE_CONFIRMACAO,
                titulo="Erro",
                mensagem="Tipo de rejeição inválido.",
                classe="error",
                cor="#dc3545",
                detalhes=None
            ), 400
    
    except Exception as e:
        print(f"[ERRO] Rejeitar cadastro: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template_string(
            TEMPLATE_CONFIRMACAO,
            titulo="Erro Interno",
            mensagem="Ocorreu um erro ao processar a rejeição. Tente novamente mais tarde.",
            classe="error",
            cor="#dc3545",
            detalhes=None
        ), 500


@aprovacao_bp.route('/pendentes', methods=['GET'])
def listar_pendentes():
    #lista todas as aprovações pendentes (para uso administrativo)
    try:
        pendentes = AprovacaoModel.listar_pendentes()
        
        return jsonify({
            "success": True,
            "pendentes": pendentes,
            "total": len(pendentes)
        }), 200
    
    except Exception as e:
        print(f"[ERRO] Listar pendentes: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": "Erro ao listar aprovações pendentes"
        }), 500