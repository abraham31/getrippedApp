import smtplib
from email.mime.text import MIMEText
from app.core.config import settings

def send_activation_email(to_email: str, activation_token: str):
    # Construir enlace
    activation_link = f"{settings.APP_URL}/activate-account?token={activation_token}"

    subject = "Activa tu cuenta"
    body = f"""
    Hola,

    Por favor activa tu cuenta usando el siguiente enlace:

    {activation_link}

    Este enlace expirará en 48 horas.
    """


    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.FROM_EMAIL, to_email, msg.as_string())
    except Exception as e:
        print(f"Error enviando email: {e}")
        raise
