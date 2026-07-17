from uuid import UUID

from app.modules.soundcloud.schemas import SoundCloudSearchResponse
from app.modules.soundcloud.services import SoundCloudSearchService
from app.modules.venues.models import VenueSettings
from fastapi import APIRouter, HTTPException, Query, status

router = APIRouter()


@router.get("/search", response_model=SoundCloudSearchResponse)
async def search_tracks(
    q: str = Query(..., min_length=1, description="Поисковый запрос (название трека, автор)"),
    venue_id: UUID = Query(..., description="ID заведения для применения фильтров модерации"),
    limit: int = Query(30, ge=1, le=100, description="Количество результатов"),
) -> SoundCloudSearchResponse:
    """
    Ищет треки в SoundCloud, отсеивает ремиксы (если не запрошены)
    и фильтрует результаты согласно настройкам заведения (блэклисты, explicit).
    """
    venue_settings = await VenueSettings.get_or_none(venue_id=venue_id)
    if not venue_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Настройки заведения не найдены",
        )

    return await SoundCloudSearchService.search_tracks(
        query=q,
        venue_id=venue_id,
        venue_settings=venue_settings,
        limit=limit,
    )
