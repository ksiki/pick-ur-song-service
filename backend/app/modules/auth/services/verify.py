from datetime import UTC, datetime

import jwt
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_verification_token
from app.modules.accounts.models import Account
from app.modules.auth.models import RefreshSession
from fastapi import HTTPException, Request, status


class VerifyService:
    @staticmethod
    async def verify_email(token: str, request: Request) -> tuple[str, str]:
        """
        Верификация email адреса аккаунта.
        Переводит аккаунт в статус верифицированного и генерирует первую пару токенов.
        """
        email = decode_verification_token(token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный или просроченный токен"
            )

        account = await Account.get_or_none(email=email)
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Бизнес-аккаунт не найден"
            )

        if not account.is_email_verified:
            account.is_email_verified = True
            await account.save(update_fields=["is_email_verified", "updated_at"])

        access_token = create_access_token(email=account.email)
        refresh_token = create_refresh_token(email=account.email)

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
