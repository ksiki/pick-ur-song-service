from urllib.parse import quote

from app.api.dependencies import get_current_active_account
from app.modules.accounts.models import Account
from app.modules.domains.services import DomainService
from app.modules.venues.models import Venue
from app.modules.venues.schemas import GetVenuesResponse, PlayerUrlResponse
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()


@router.get(
    "/",
    response_model=GetVenuesResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить мета данные заведений",
    description="Отдает метаданные всех заведений привязанных к этому аккаунту",
)
async def get_all_venues(
    current_account: Account = Depends(get_current_active_account),
) -> GetVenuesResponse:
    venues = await Venue.filter(account=current_account, is_active=True)

    if not venues:
        return GetVenuesResponse(venues=[])

    return GetVenuesResponse(venues=venues)  # type: ignore[arg-type]


@router.get(
    "/{venue_id}/player-url",
    response_model=PlayerUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить URL технического домена для плеера",
    description="Запускает алгоритм балансировки, назначает домен и выдает ссылку с JWT-токеном.",
)
async def get_player_url(
    venue_id: str,
    current_account: Account = Depends(get_current_active_account),
) -> PlayerUrlResponse:
    venue = await Venue.get_or_none(id=venue_id, account=current_account)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заведение не найдено или у вас нет к нему доступа",
        )

    if not venue.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Данное заведение отключено"
        )

    assigned_domain = await DomainService.assign_domain_to_venue(venue)

    token = DomainService.generate_player_token(venue)

    # 4. Формируем финальную ссылку (предполагается, что domain.url уже содержит https://)
    # Пример: https://dash-1.xyz/player?token=eyJhbG...
    player_url = (
        f"{assigned_domain.url}/player"
        f"?token={quote(str(token))}"
        f"&venue_id={quote(str(venue.id))}"
        f"&venue_name={quote(venue.name)}"
        f"&address={quote(venue.address)}"
    )

    return PlayerUrlResponse(url=player_url)
