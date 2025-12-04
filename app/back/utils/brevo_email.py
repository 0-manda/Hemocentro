import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from config.config import Config

# Configurar API do Brevo
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = Config.BREVO_API_KEY

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)

def enviar_email_brevo(destinatario, nome_destinatario, assunto, html_content):
    """
    Envia email usando Brevo (Sendinblue)
    
    Args:
        destinatario: Email do destinatário (ex: 'admin@email.com')
        nome_destinatario: Nome do destinatário (ex: 'João Silva')
        assunto: Assunto do email
        html_content: Conteúdo HTML do email
    
    Returns:
        bool: True se enviou com sucesso, False caso contrário
    """
    try:
        # Separar nome e email do remetente
        from_name = "Sistema Hemocentro"
        from_email = Config.EMAIL_FROM
        
        # Se EMAIL_FROM está no formato "Nome <email>"
        if "<" in from_email:
            parts = from_email.split("<")
            from_name = parts[0].strip()
            from_email = parts[1].replace(">", "").strip()
        
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            to=[{"email": destinatario, "name": nome_destinatario}],
            sender={"email": from_email, "name": from_name},
            subject=assunto,
            html_content=html_content
        )
        
        response = api_instance.send_transac_email(send_smtp_email)
        print(f"[INFO] Email enviado com sucesso para {destinatario} - Message ID: {response.message_id}")
        return True
        
    except ApiException as e:
        print(f"[ERRO] Erro ao enviar email via Brevo: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"[ERRO] Erro inesperado ao enviar email: {e}")
        import traceback
        traceback.print_exc()
        return False