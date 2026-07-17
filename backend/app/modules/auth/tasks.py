# ваш файл с роутером
from app.core.config import settings
from app.core.email import send_email
from faststream.rabbit import RabbitRouter

auth_router = RabbitRouter()


@auth_router.subscriber("verification_queue")
async def send_verification_message(email: str, token: str) -> None:
    """
    Фоновая задача для отправки Email с подтверждением
    """
    verification_link = f"http://{settings.DOMEN}/auth/verify?token={token}"

    html_content = f"""
    <h2>Добро пожаловать!</h2>
    <p>Чтобы подтвердить регистрацию, перейдите по ссылке ниже:</p>
    <a href="{verification_link}">Подтвердить email</a>
    """

    await send_email(to_email=email, subject="Подтверждение регистрации", html_content=html_content)
    print(f"[УСПЕХ] Письмо верификации ушло на {email}")


@auth_router.subscriber("otp_queue")
async def send_otp_message(email: str, code: str) -> None:
    """
    Фоновая задача для отправки OTP кода на почту.
    """
    html_content = f"""
    <h2>Ваш код авторизации</h2>
    <p>Никому не сообщайте этот код.</p>
    <h1 style="color: #4CAF50; letter-spacing: 5px;">{code}</h1>
    """

    await send_email(to_email=email, subject="Код для входа", html_content=html_content)
    print(f"[УСПЕХ] OTP письмо ушло на {email}")
