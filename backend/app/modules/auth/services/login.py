from datetime import UTC, datetime

import jwt
from app.broker.client import broker
from app.core.config import settings
from app.core.redis import redis_cache
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_otp_code,
    verify_password,
)
from app.modules.accounts.models import Account
from app.modules.auth.models import RefreshSession
from app.modules.auth.schemas import AccountLogin, VerifyOTPRequest
from fastapi import HTTPException, Request, status


class LoginService:
    @staticmethod
    async def initiate_login(data: AccountLogin) -> None:
        """
        Этап 1: Проверка пароля бизнес-аккаунта и инициация OTP.
        """
        account = await Account.get_or_none(email=data.email)

        if not account or not verify_password(data.password, account.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль"
            )

        if not account.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email не подтвержден. Пожалуйста, проверьте почту.",
            )

        otp_code = generate_otp_code()
        redis_key = f"otp:{account.email}"

        await redis_cache.safe_client.set(
            name=redis_key,
            value=otp_code,
            ex=300,
        )

        await broker.publish(
            message={"email": account.email, "code": otp_code},
            queue="otp_queue",
        )

    @staticmethod
    async def verify_otp(data: VerifyOTPRequest, request: Request) -> tuple[str, str]:
        """
        Этап 2: Проверка OTP и генерация пары токенов для аккаунта.
        Возвращает tuple: (access_token, refresh_token)
        """
        redis_key = f"otp:{data.email}"
        saved_code = await redis_cache.safe_client.get(name=redis_key)

        if not saved_code or saved_code != data.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный или истекший код подтверждения",
            )

        await redis_cache.safe_client.delete(redis_key)

        account = await Account.get(email=data.email)

        access_token = create_access_token(email=data.email)
        refresh_token = create_refresh_token(email=data.email)

        client_ip = request.headers.get("X-Forwarded-For")
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "Unknown"

        user_agent = request.headers.get("User-Agent", "Unknown Device")
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        await RefreshSession.create(
            account=account,
            refresh_token_jti=payload["jti"],
            user_agent=user_agent[:512],
            ip_address=client_ip[:45],
            expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
        )

        return access_token, refresh_token
