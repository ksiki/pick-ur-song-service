from datetime import UTC, datetime

from app.core.security import get_password_hash
from app.modules.accounts.models import Account
from app.modules.auth.schemas import AccountOnboarding
from app.modules.venues.models import Venue
from fastapi import Request
from tortoise.transactions import in_transaction


class OnboardingService:
    @staticmethod
    async def complete_onboarding(
        data: AccountOnboarding, current_account: Account, request: Request
    ) -> None:
        client_ip = request.headers.get("X-Forwarded-For")
        if client_ip:
            client_ip = client_ip.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "Unknown"

        passcode_hash = get_password_hash(data.admin_passcode)

        async with in_transaction():
            current_account.legal_name = data.legal_name
            current_account.unp = data.unp
            current_account.iban = data.iban

            if not current_account.offer_accepted_at:
                current_account.offer_accepted_at = datetime.now(UTC)
                current_account.offer_accepted_ip = client_ip

            current_account.is_active = True
            await current_account.save()

            await Venue.create(
                account=current_account,
                name=data.venue_name,
                number=data.venue_number,
                address=data.address,
                admin_passcode_hash=passcode_hash,
                player_is_active=False,
                is_active=True,
            )
