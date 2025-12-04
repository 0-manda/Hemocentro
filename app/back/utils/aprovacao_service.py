import secrets
from config.config import Config
from back.models.aprovacao_model import AprovacaoModel
from back.models import UsuarioModel, HemocentroModel
from back.utils.brevo_email import enviar_email_brevo

def gerar_token_aprovacao():
    return secrets.token_urlsafe(32)

def criar_solicitacao_aprovacao(tipo, id_entidade, email_destino, dados_entidade=None):
    try:
        token = gerar_token_aprovacao()
        AprovacaoModel.criar_token(tipo, id_entidade, token)
        enviar_email_solicitacao(tipo, id_entidade, token, email_destino, dados_entidade)
        return True
    except Exception as e:
        print(f"[ERRO] Criar solicitação de aprovação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def enviar_email_solicitacao(tipo, id_entidade, token, email_destino, dados_entidade=None):
    try:
        # determinar tipo e detalhes da entidade
        if tipo == 'doador':
            entidade = UsuarioModel.buscar_por_id(id_entidade)
            tipo_label = "Doador"
            nome_destinatario = "Administrador"
            detalhes = f"""
                <p><strong>Nome:</strong> {entidade['nome']}</p>
                <p><strong>Email:</strong> {entidade['email']}</p>
                <p><strong>Telefone:</strong> {entidade.get('telefone', 'N/A')}</p>
                <p><strong>CPF:</strong> {entidade.get('cpf', 'N/A')}</p>
                <p><strong>Tipo Sanguíneo:</strong> {entidade.get('tipo_sanguineo', 'Não informado')}</p>
                <p><strong>Data de Nascimento:</strong> {entidade.get('data_nascimento', 'N/A')}</p>
            """
        elif tipo == 'colaborador':
            entidade = UsuarioModel.buscar_por_id(id_entidade)
            tipo_label = "Colaborador"
            nome_destinatario = "Hemocentro"
            detalhes = f"""
                <p><strong>Nome:</strong> {entidade['nome']}</p>
                <p><strong>Email:</strong> {entidade['email']}</p>
                <p><strong>Telefone:</strong> {entidade.get('telefone', 'N/A')}</p>
                <p><strong>CNPJ:</strong> {entidade.get('cnpj', 'N/A')}</p>
            """
            # adicionar CPF se fornecido
            if entidade.get('cpf'):
                detalhes += f"""
                <p><strong>CPF:</strong> {entidade.get('cpf')}</p>
                """
            # adicionar nome do hemocentro
            if dados_entidade and 'hemocentro_nome' in dados_entidade:
                detalhes += f"""
                    <p><strong>Hemocentro:</strong> {dados_entidade['hemocentro_nome']}</p>
                """
        else:  # hemocentro
            entidade = HemocentroModel.buscar_por_id(id_entidade)
            tipo_label = "Hemocentro"
            nome_destinatario = "Administrador"
            detalhes = f"""
                <p><strong>Nome:</strong> {entidade['nome']}</p>
                <p><strong>Email:</strong> {entidade['email']}</p>
                <p><strong>CNPJ:</strong> {entidade['cnpj']}</p>
                <p><strong>Telefone:</strong> {entidade.get('telefone', 'N/A')}</p>
                <p><strong>Endereço:</strong> {entidade.get('endereco', 'N/A')}</p>
                <p><strong>Cidade:</strong> {entidade.get('cidade', 'N/A')} - {entidade.get('estado', 'N/A')}</p>
            """
        # URLs de aprovação
        base_url = Config.BASE_URL or "http://localhost:5000"
        url_aprovar = f"{base_url}/api/aprovacao/aprovar/{token}"
        url_rejeitar = f"{base_url}/api/aprovacao/rejeitar/{token}"
        # template do email
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nova Solicitação de Cadastro</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">Nova Solicitação de Cadastro</h1>
            </header>
            <main style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <h2 style="color: #667eea; margin-top: 0;">Tipo: {tipo_label}</h2>
                <section style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">Detalhes do Cadastro:</h3>
                    {detalhes}
                </section>
                <p style="font-size: 16px; margin: 25px 0;">
                    {'Um novo doador' if tipo == 'doador' else f'Um novo {tipo_label.lower()}'} está aguardando aprovação para acessar o sistema.
                    Por favor, revise as informações acima e escolha uma das ações abaixo:
                </p>
                <nav style="text-align: center; margin: 30px 0;">
                    <a href="{url_aprovar}" 
                       style="background: #28a745; color: white; padding: 15px 40px; text-decoration: none; 
                              border-radius: 5px; display: inline-block; margin: 10px; font-weight: bold;">
                        APROVAR CADASTRO
                    </a>
                    <a href="{url_rejeitar}" 
                       style="background: #dc3545; color: white; padding: 15px 40px; text-decoration: none; 
                              border-radius: 5px; display: inline-block; margin: 10px; font-weight: bold;">
                        REJEITAR CADASTRO
                    </a>
                </nav>
                <aside style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px;">
                    <p style="margin: 0; color: #856404;">
                        <strong>Importante:</strong> Este link expira em 7 dias. 
                        Após esse período, será necessário gerar uma nova solicitação.
                    </p>
                </aside>
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            </main>
            <footer style="font-size: 12px; color: #666; text-align: center;">
                <p style="margin: 0;">
                    Este é um email automático, por favor não responda.<br>
                    Se você não {'é um administrador' if tipo != 'colaborador' else 'representa este hemocentro'}, ignore esta mensagem.
                </p>
            </footer>  
        </body>
        </html>
        """
        # enviar via Brevo
        sucesso = enviar_email_brevo(
            destinatario=email_destino,
            nome_destinatario=nome_destinatario,
            assunto=f"Nova Solicitação de Cadastro - {tipo_label}",
            html_content=html_content
        ) 
        if sucesso:
            print(f"[INFO] Email de solicitação enviado para {email_destino}")
        else:
            print(f"[ERRO] Falha ao enviar email de solicitação para {email_destino}")
            raise Exception("Falha ao enviar email via Brevo") 
    except Exception as e:
        print(f"[ERRO] Enviar email de solicitação: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def reenviar_solicitacao_aprovacao(tipo, id_entidade, email_destino, dados_entidade=None):
    try:
        return criar_solicitacao_aprovacao(tipo, id_entidade, email_destino, dados_entidade)
    except Exception as e:
        print(f"[ERRO] Reenviar solicitação: {str(e)}")
        return False

def verificar_status_aprovacao(tipo, id_entidade):
    try:
        from back.models import UsuarioModel, HemocentroModel     
        if tipo == 'doador' or tipo == 'colaborador':
            entidade = UsuarioModel.buscar_por_id(id_entidade)
        else:  # hemocentro
            entidade = HemocentroModel.buscar_por_id(id_entidade)
        if not entidade:
            return {
                "existe": False,
                "ativo": False,
                "mensagem": "Entidade não encontrada"
            }
        return {
            "existe": True,
            "ativo": entidade.get('ativo', False),
            "mensagem": "Ativo" if entidade.get('ativo', False) else "Aguardando aprovação"
        }
    except Exception as e:
        print(f"[ERRO] Verificar status: {str(e)}")
        return {
            "existe": False,
            "ativo": False,
            "mensagem": "Erro ao verificar status"
        }

def limpar_tokens_expirados():
    try:
        return AprovacaoModel.limpar_tokens_expirados()
    except Exception as e:
        print(f"[ERRO] Limpar tokens expirados: {str(e)}")
        return 0