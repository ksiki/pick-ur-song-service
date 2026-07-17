import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import uuid6
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

from app.core.config import settings

pwd_context = PasswordHash((BcryptHasher(),))


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_otp_code() -> str:
    return "".join(secrets.choice("0123456789") for _ in range(6))


def create_jwt_token(subject: str, expires_delta: timedelta, token_type: str) -> str:
    expire = datetime.now(UTC) + expires_delta
    payload = {
        "sub": subject,
        "exp": expire,
        "type": token_type,
        "jti": str(uuid6.uuid7),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(email: str) -> str:
    """Создает короткоживущий Access Token для REST/WebSocket"""
    return create_jwt_token(
        subject=email,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",  # noqa: S106
    )


def create_refresh_token(email: str) -> str:
    """Создает долгоживущий Refresh Token для обновления сессии"""
    return create_jwt_token(
        subject=email,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",  # noqa: S106
    )


def create_verification_token(email: str) -> str:
    """
    Создает JWT токен для подтверждения почты.
    В payload зашиваем email ('sub'), срок действия ('exp') и тип токена ('type')
    """
    expire = datetime.now(UTC) + timedelta(hours=settings.EMAIL_TOKEN_EXPIRE_HOURS)

    payload = {
        "sub": email,
        "exp": expire,
        "type": "email_verification",
    }

    encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_verification_token(token: str) -> str | None:
    """
    Расшифровывает токен и возвращает email, если токен валиден.
    Если токен истек, возвращает None.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type") != "email_verification":
            return None

        email: str = str(payload.get("sub"))
        if email is None:
            return None

        return email

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """
    Расшифровывает Refresh Token и возвращает весь payload, если токен валиден.
    Если токен истек, подделан или имеет неверный тип, возвращает None.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
