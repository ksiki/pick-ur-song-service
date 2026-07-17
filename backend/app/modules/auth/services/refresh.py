from datetime import UTC, datetime

import jwt
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_refresh_token
from app.modules.auth.models import RefreshSession
from fastapi import HTTPException, Request, status


class RefreshService:
    @staticmethod
    async def refresh_session(token: str | None, request: Request) -> tuple[str, str]:
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token отсутствует. Необходима повторная авторизация.",
            )

        payload = decode_refresh_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный или просроченный refresh token. Необходима повторная авторизация.",
            )

        old_jti = payload.get("jti")

        session = await RefreshSession.get_or_none(refresh_token_jti=old_jti).prefetch_related(
            "account"
        )

        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Сессия была завершена. Выполните вход заново.",
            )

        account = session.account

        new_access_token = create_access_token(email=account.email)
        new_refresh_token = create_refresh_token(email=account.email)

        client_ip = request.headers.get("X-Forwarded-For")
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "Unknown"

        user_agent = request.headers.get("User-Agent", "Unknown Device")

        new_payload = jwt.decode(
            new_refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        session.refresh_token_jti = new_payload["jti"]
        session.expires_at = datetime.fromtimestamp(new_payload["exp"], tz=UTC)
        session.ip_address = client_ip[:45]
        session.user_agent = user_agent[:512]

        await session.save()

        return new_access_token, new_refresh_token
