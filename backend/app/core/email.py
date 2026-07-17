from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings


async def send_email(to_email: str, subject: str, html_content: str) -> None:
    """
    Универсальная асинхронная функция для отправки писем.
    """
    message = EmailMessage()
    message["From"] = settings.SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(html_content, subtype="html")

    kwargs = {
        "hostname": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "use_tls": False,
    }

    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        kwargs["username"] = settings.SMTP_USER
        kwargs["password"] = settings.SMTP_PASSWORD
        kwargs["start_tls"] = True

    await aiosmtplib.send(message, **kwargs)  # type: ignore[arg-type]
