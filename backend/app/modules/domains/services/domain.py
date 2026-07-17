from datetime import UTC, datetime, timedelta

import jwt
from app.core.config import settings
from app.modules.domains.models import PlayerDomain
from app.modules.venues.models import Venue
from fastapi import HTTPException, status


class DomainService:
    @staticmethod
    async def assign_domain_to_venue(venue: Venue) -> PlayerDomain:
        """
        Алгоритм назначения технического домена заведению.
        Балансирует нагрузку и проверяет блокировки.
        """

        await venue.fetch_related("assigned_domain")
        current_domain = venue.assigned_domain

        if current_domain and current_domain.is_active and not current_domain.is_banned:
            return current_domain

        active_domains = await PlayerDomain.filter(is_active=True, is_banned=False).all()

        selected_domain = None
        for domain in active_domains:
            current_load = await domain.venues.all().count()  # type: ignore[attr-defined]
            if current_load < domain.max_capacity:
                selected_domain = domain
                break

        if not selected_domain:
            # TODO: Здесь в будущем добавим вызов воркера/брокера для критического алерта
            print("[CRITICAL] Пул доменов исчерпан или все забанены!")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Нет доступных серверов для плеера. Администрация уже решает проблему.",
            )

        venue.assigned_domain = selected_domain
        await venue.save(update_fields=["assigned_domain_id", "updated_at"])

        return selected_domain

    @staticmethod
    def generate_player_token(venue: Venue) -> str:
        """
        Генерирует сессионный JWT-токен для iframe плеера на 12 часов (рабочая смена).
        """
        expire = datetime.now(UTC) + timedelta(hours=12)
        payload = {
            "sub": str(venue.id),
            "type": "player_iframe",
            "exp": expire,
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
