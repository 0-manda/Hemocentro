from config.config import Config
from back.utils.brevo_email import enviar_email_brevo

def enviar_notificacao_aprovacao(email_destinatario, nome_usuario, tipo_entidade):
    """Envia email notificando que o cadastro foi aprovado"""
    try:
        if tipo_entidade == 'doador':
            tipo_label = "Doador"
            mensagem_extra = "Agora você pode fazer login e agendar suas doações de sangue!"
        elif tipo_entidade == 'colaborador':
            tipo_label = "Colaborador"
            mensagem_extra = "Agora você pode fazer login e gerenciar as doações do seu hemocentro!"
        else:
            tipo_label = "Hemocentro"
            mensagem_extra = "Seu hemocentro agora está visível no sistema e pode receber agendamentos!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cadastro Aprovado</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            
            <header style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">Cadastro Aprovado!</h1>
            </header>
            
            <main style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 18px; color: #333;">
                    Olá, <strong>{nome_usuario}</strong>!
                </p>
                
                <p style="font-size: 16px; margin: 20px 0;">
                    Temos uma ótima notícia!
                </p>
                
                <section style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745; margin: 20px 0;">
                    <p style="font-size: 16px; margin: 0;">
                        Seu cadastro como <strong>{tipo_label}</strong> foi aprovado pelo nosso time!
                    </p>
                </section>
                
                <p style="font-size: 16px; margin: 20px 0;">
                    {mensagem_extra}
                </p>
                
                <nav style="text-align: center; margin: 30px 0;">
                    <a href="{Config.BASE_URL or 'http://localhost:5000'}/login" 
                       style="background: #28a745; color: white; padding: 15px 40px; text-decoration: none; 
                              border-radius: 5px; display: inline-block; font-weight: bold;">
                        Acessar Plataforma
                    </a>
                </nav>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="font-size: 14px; color: #666;">
                    Obrigado por fazer parte da nossa comunidade de doadores de sangue!<br>
                    Juntos, salvamos vidas.
                </p>
            </main>
            
            <footer style="font-size: 12px; color: #999; text-align: center; margin-top: 20px;">
                <p style="margin: 0;">Este é um email automático, por favor não responda.</p>
            </footer>
            
        </body>
        </html>
        """
        
        # Enviar via Brevo
        sucesso = enviar_email_brevo(
            destinatario=email_destinatario,
            nome_destinatario=nome_usuario,
            assunto=f"Seu cadastro foi aprovado - {tipo_label}",
            html_content=html_content
        )
        
        if sucesso:
            print(f"[INFO] Email de aprovação enviado para {email_destinatario}")
        else:
            print(f"[ERRO] Falha ao enviar email de aprovação para {email_destinatario}")
        
        return sucesso
        
    except Exception as e:
        print(f"[ERRO] Enviar notificação de aprovação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def enviar_notificacao_rejeicao(email_destinatario, nome_usuario, tipo_entidade, motivo=None):
    """Envia email notificando que o cadastro foi rejeitado"""
    try:
        if tipo_entidade == 'doador':
            tipo_label = "Doador"
        elif tipo_entidade == 'colaborador':
            tipo_label = "Colaborador"
        else:
            tipo_label = "Hemocentro"
        
        motivo_texto = motivo or "Não foi possível aprovar seu cadastro no momento."
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cadastro Não Aprovado</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            
            <header style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); padding: 30px; border-radius: 10px 10px 0 0; text-align: center;">
                <h1 style="color: white; margin: 0;">Cadastro Não Aprovado</h1>
            </header>
            
            <main style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 18px; color: #333;">
                    Olá, <strong>{nome_usuario}</strong>!
                </p>
                
                <p style="font-size: 16px; margin: 20px 0;">
                    Infelizmente, seu cadastro como <strong>{tipo_label}</strong> não foi aprovado.
                </p>
                
                <section style="background: white; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545; margin: 20px 0;">
                    <p style="font-size: 16px; margin: 0; color: #666;">
                        <strong>Motivo:</strong><br>
                        {motivo_texto}
                    </p>
                </section>
                
                <p style="font-size: 16px; margin: 20px 0;">
                    Se você acredita que houve um erro, por favor entre em contato conosco.
                </p>
                
                <nav style="text-align: center; margin: 30px 0;">
                    <a href="{Config.BASE_URL or 'http://localhost:3000'}/contato" 
                       style="background: #667eea; color: white; padding: 15px 40px; text-decoration: none; 
                              border-radius: 5px; display: inline-block; font-weight: bold;">
                        Fale Conosco
                    </a>
                </nav>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            </main>
            
            <footer style="font-size: 12px; color: #999; text-align: center;">
                <p style="margin: 0;">Este é um email automático, por favor não responda.</p>
            </footer>
            
        </body>
        </html>
        """
        
        # Enviar via Brevo
        sucesso = enviar_email_brevo(
            destinatario=email_destinatario,
            nome_destinatario=nome_usuario,
            assunto=f"Seu cadastro não foi aprovado - {tipo_label}",
            html_content=html_content
        )
        
        if sucesso:
            print(f"[INFO] Email de rejeição enviado para {email_destinatario}")
        else:
            print(f"[ERRO] Falha ao enviar email de rejeição para {email_destinatario}")
        
        return sucesso
        
    except Exception as e:
        print(f"[ERRO] Enviar notificação de rejeição: {str(e)}")
        import traceback
        traceback.print_exc()
        return False