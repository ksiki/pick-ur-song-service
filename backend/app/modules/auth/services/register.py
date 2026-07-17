from app.broker.client import broker
from app.core.security import create_verification_token, get_password_hash
from app.modules.accounts.models import Account
from app.modules.auth.schemas import AccountCreate
from fastapi import HTTPException, status
from tortoise.transactions import in_transaction


class RegisterService:
    @staticmethod
    async def register_account(data: AccountCreate) -> Account:
        """
        Регистрация нового бизнес-аккаунта (владельца).
        Создает неактивный аккаунт и отправляет токен верификации в очередь для отправки email.
        """
        if await Account.filter(email=data.email).exists():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже занят")

        hashed_password = get_password_hash(data.password)

        async with in_transaction():
            new_account = await Account.create(
                email=data.email,
                password_hash=hashed_password,
                is_active=False,
                is_email_verified=False,
            )

            token = create_verification_token(email=new_account.email)

            await broker.publish(
                message={"email": new_account.email, "token": token},
                queue="verification_queue",
            )

        return new_account
