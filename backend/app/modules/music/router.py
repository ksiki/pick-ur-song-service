from app.api.dependencies import get_current_active_account
from app.modules.accounts.models import Account
from app.modules.auth.schemas import MessageResponse
from app.modules.music.models import VenueBlacklist
from app.modules.music.schemas import AddBlacklistRequest, BlacklistItemResponse
from app.modules.venues.models import Venue
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import UUID4

router = APIRouter()


@router.post(
    "/queue/blacklist",
    response_model=BlacklistItemResponse,
    summary="Добавить правило в черный список",
    description="Добавляет артиста или ключевое слово для алгоритмической модерации.",
)
async def add_to_blacklist(
    request: AddBlacklistRequest,
    current_account: Account = Depends(get_current_active_account),
) -> BlacklistItemResponse:
    venue = await Venue.get_or_none(id=request.venue_id, account=current_account)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Заведение не найдено или у вас нет к нему доступа.",
        )

    exists = await VenueBlacklist.filter(
        venue=venue, item_type=request.item_type, item_value=request.item_value
    ).exists()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Это правило уже существует в черном списке данного заведения.",
        )

    item = await VenueBlacklist.create(
        venue=venue, item_type=request.item_type, item_value=request.item_value
    )

    return item  # type: ignore[return-value]


@router.get(
    "/queue/blacklist",
    response_model=list[BlacklistItemResponse],
    summary="Получить черный список бара",
    description="Возвращает все стоп-слова и заблокированных артистов для дашборда.",
)
async def get_blacklist(
    venue_id: UUID4 = Query(..., description="ID заведения"),
    current_account: Account = Depends(get_current_active_account),
) -> list[BlacklistItemResponse]:
    venue = await Venue.get_or_none(id=venue_id, account=current_account)
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Заведение не найдено или у вас нет к нему доступа.",
        )

    items = await VenueBlacklist.filter(venue=venue).all()
    return items  # type: ignore[return-value]


@router.delete(
    "/queue/blacklist/{item_id}",
    response_model=MessageResponse,
    summary="Удалить правило из черного списка",
)
async def delete_from_blacklist(
    item_id: UUID4,
    current_account: Account = Depends(get_current_active_account),
) -> MessageResponse:
    item = await VenueBlacklist.get_or_none(id=item_id).prefetch_related("venue")
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Правило не найдено.")

    if item.venue.account.id != current_account.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на удаление этого правила.",
        )

    await item.delete()
    return MessageResponse(message="Правило успешно удалено")
