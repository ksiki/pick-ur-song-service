from datetime import UTC, datetime

from app.api.dependencies import get_current_account, get_current_active_account
from app.core.security import decode_refresh_token
from app.modules.accounts.models.account import Account
from app.modules.auth.models import RefreshSession
from app.modules.auth.schemas import (
    AccountCreate,
    AccountLogin,
    AccountOnboarding,
    LoginOTPRequiredResponse,
    MessageResponse,
    SessionResponse,
    TokenResponse,
    VerifyEmailRequest,
    VerifyOTPRequest,
)
from app.modules.auth.services import (
    LoginService,
    OnboardingService,
    RefreshService,
    RegisterService,
    VerifyService,
)
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status

router = APIRouter()


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Шаг 1: Базовая регистрация бизнес-аккаунта",
    description="Создает неактивный аккаунт владельца и отправляет ссылку на почту.",
)
async def register(account_in: AccountCreate) -> MessageResponse:
    await RegisterService.register_account(data=account_in)
    return MessageResponse(message="Регистрация успешна. Проверьте почту для подтверждения.")


@router.post(
    "/verify-email",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Шаг 2: Верификация почты",
    description="Принимает токен из письма, подтверждает email аккаунта и авторизует пользователя.",
)
async def verify_email(
    payload: VerifyEmailRequest, request: Request, response: Response
) -> TokenResponse:
    access_token, refresh_token = await VerifyService.verify_email(
        token=payload.token, request=request
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # Только LocalHost (в прод переключить на True)
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return TokenResponse(access_token=access_token)


@router.post(
    "/onboarding",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Шаг 3: Юридический онбординг сети",
    description="""Принимает юридические данные аккаунта, фиксирует акцепт оферты,
    активирует профиль владельца и создает первое заведение. Требует авторизации.""",
)
async def onboarding(
    request: Request,
    data: AccountOnboarding,
    current_account: Account = Depends(get_current_account),
) -> MessageResponse:
    await OnboardingService.complete_onboarding(
        data=data, current_account=current_account, request=request
    )
    return MessageResponse(
        message="Данные успешно сохранены. Первая точка сети создана и активирована."
    )


@router.post(
    "/login",
    response_model=LoginOTPRequiredResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация аккаунта: Этап 1",
    description="Проверяет пароль владельца и отправляет 6-значный OTP код на email.",
)
async def login(credentials: AccountLogin) -> LoginOTPRequiredResponse:
    await LoginService.initiate_login(data=credentials)
    return LoginOTPRequiredResponse(email=credentials.email)


@router.post(
    "/login/verify",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Авторизация аккаунта: Этап 2 (Проверка OTP)",
    description="""Проверяет OTP код из Redis.
    Возвращает Access Token аккаунта, а Refresh Token зашивает в HttpOnly Cookie.""",
)
async def verify_login_otp(
    payload: VerifyOTPRequest, request: Request, response: Response
) -> TokenResponse:
    access_token, refresh_token = await LoginService.verify_otp(data=payload, request=request)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return TokenResponse(access_token=access_token)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Обновление сессии аккаунта (Token Rotation)",
    description="""Принимает refresh_token из Cookie,
    выдает новый access_token и заменяет refresh_token в Cookie.""",
)
async def refresh_token(
    request: Request, response: Response, refresh_token: str | None = Cookie(default=None)
) -> TokenResponse:
    new_access, new_refresh = await RefreshService.refresh_session(
        token=refresh_token, request=request
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return TokenResponse(access_token=new_access)


@router.get(
    "/sessions",
    response_model=list[SessionResponse],
    summary="Получить список активных сессий аккаунта",
)
async def get_active_sessions(
    current_account: Account = Depends(get_current_active_account),
) -> list[SessionResponse]:
    sessions = await RefreshSession.filter(
        account=current_account, expires_at__gt=datetime.now(UTC)
    ).all()
    return sessions  # type: ignore[return-value]


@router.delete(
    "/sessions/{session_id}",
    response_model=MessageResponse,
    summary="Завершить конкретную сессию аккаунта",
)
async def terminate_session(
    session_id: str, current_account: Account = Depends(get_current_active_account)
) -> MessageResponse:
    deleted_count = await RefreshSession.filter(id=session_id, account=current_account).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    return MessageResponse(message="Сессия успешно завершена")


@router.delete(
    "/sessions",
    response_model=MessageResponse,
    summary="Выйти со всех остальных устройств аккаунта",
)
async def terminate_all_other_sessions(
    request: Request,
    current_account: Account = Depends(get_current_active_account),
) -> MessageResponse:
    current_refresh_token = request.cookies.get("refresh_token")

    if current_refresh_token is None:
        raise HTTPException(status_code=401, detail="Token missing")

    payload = decode_refresh_token(current_refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    current_jti = payload.get("jti") if current_refresh_token else None

    query = RefreshSession.filter(account=current_account)
    if current_jti:
        query = query.exclude(refresh_token_jti=current_jti)

    await query.delete()
    return MessageResponse(message="Все остальные сессии аккаунта принудительно закрыты")
