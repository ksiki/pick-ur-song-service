from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Query, Security, WebSocketException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer

from app.core.config import settings
from app.modules.accounts.models import Account
from app.modules.venues.models import Venue

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
token_auth_scheme = HTTPBearer(description="JWT-токен плеера (выдается мастер-шлюзом)")


async def get_current_account(token: Annotated[str, Depends(oauth2_scheme)]) -> Account:
    """
    Базовая зависимость аутентификации.
    Проверяет валидность Access Token и возвращает объект бизнес-аккаунта.
    Используется для эндпоинтов, доступных ДО завершения онбординга (например, /onboarding).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type") != "access":
            raise credentials_exception

        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception

    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        raise credentials_exception from None

    account = await Account.get_or_none(email=email)
    if account is None:
        raise credentials_exception

    return account


async def get_current_active_account(
    current_account: Annotated[Account, Depends(get_current_account)],
) -> Account:
    """
    Строгая зависимость аутентификации.
    Проверяет, прошел ли аккаунт юридический онбординг (is_active=True).
    Защищает все основные бизнес-эндпоинты системы.
    """
    if not current_account.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт не активирован. Необходимо завершить юридический онбординг.",
        )
    return current_account


async def get_current_player_venue(
    credentials: HTTPAuthorizationCredentials = Security(token_auth_scheme),
) -> Venue:
    """
    Зависимость для аутентификации iframe-плеера.
    Проверяет валидность токена 'player_iframe' и возвращает объект заведения.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный или просроченный токен плеера",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type") != "player_iframe":
            raise credentials_exception

        venue_id_str: str | None = payload.get("sub")
        if not venue_id_str:
            raise credentials_exception

    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        raise credentials_exception from None

    venue = await Venue.get_or_none(id=venue_id_str)

    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заведение, привязанное к этому плееру, не найдено",
        )

    if not venue.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Данное заведение было отключено. Плеер заблокирован.",
        )

    return venue


async def get_ws_player_venue(
    token: str = Query(..., description="JWT токен плеера (передается в URL)"),
) -> Venue:
    """
    Специальная зависимость для WebSocket.
    Читает токен из Query-параметров, так как браузерный WS не поддерживает заголовки.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type") != "player_iframe":
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

        venue_id_str = payload.get("sub")
        if not venue_id_str:
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION) from None

    venue = await Venue.get_or_none(id=venue_id_str)

    if not venue or not venue.is_active:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    return venue
