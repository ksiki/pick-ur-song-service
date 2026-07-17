import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class MessageResponse(BaseModel):
    """Универсальная схема для успешных действий без возврата сущности."""

    message: str


class AccountCreate(BaseModel):
    """Схема для первого шага: базовая регистрация бизнес-аккаунта."""

    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8, max_length=64)


class AccountLogin(BaseModel):
    """Схема для входа в бизнес-аккаунт."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Схема для выдачи JWT-токенов фронтенду."""

    access_token: str
    token_type: str = "bearer"


class VerifyEmailRequest(BaseModel):
    token: str


class AccountOnboarding(BaseModel):
    """
    Схема для шага онбординга.
    Заполняет юридические данные аккаунта и создает первое заведение.
    """

    legal_name: str = Field(
        ..., max_length=255, description="Юридическое лицо (ИП Иванов И.И. / ООО 'Бар')"
    )
    unp: str = Field(..., min_length=9, max_length=9, description="УНП (строго 9 цифр)")
    iban: str = Field(..., min_length=28, max_length=28, description="Расчетный счет (IBAN)")

    venue_name: str = Field(
        ..., max_length=255, description="Коммерческое название первого заведения"
    )
    venue_number: str = Field(
        ..., min_length=9, max_length=15, description="Номер телефона заведения с кодом страны"
    )
    address: str = Field(max_length=255, description="Адрес вида: Беларусь, Гомель, Советская, 34")
    admin_passcode: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="Кодовая фраза для доступа к админской зоне плеера",
    )

    @field_validator("unp")
    @classmethod
    def validate_unp(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("УНП должен состоять исключительно из цифр")
        return value

    @field_validator("iban")
    @classmethod
    def validate_iban(cls, value: str) -> str:
        # Валидация белорусского IBAN: BY + 2 цифры + 4 буквы банка + 20 цифр счета
        pattern = r"^BY\d{2}[A-Z0-9]{4}\d{20}$"
        cleaned_value = value.replace(" ", "").upper()
        if not re.match(pattern, cleaned_value):
            raise ValueError("Некорректный формат IBAN для Республики Беларусь")
        return cleaned_value


class LoginOTPRequiredResponse(BaseModel):
    """Ответ сервера, указывающий, что пароль верен и требуется ввод OTP"""

    message: str = "Код подтверждения отправлен на почту"
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    """Схема для отправки кода подтверждения."""

    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description="6-значный код из письма")


class SessionResponse(BaseModel):
    """Схема для отображения активной сессии в интерфейсе."""

    id: UUID
    user_agent: str
    ip_address: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)
