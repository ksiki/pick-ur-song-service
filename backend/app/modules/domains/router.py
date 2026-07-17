from app.api.dependencies import get_current_player_venue
from app.broker.client import broker
from app.modules.domains.models import PlayerDomain
from app.modules.domains.schemas import ReportBanRequest, ReportBanResponse
from app.modules.domains.services import DomainService
from app.modules.venues.models import Venue
from fastapi import APIRouter, Depends, status

router = APIRouter()


@router.post(
    "/report-ban",
    response_model=ReportBanResponse,
    status_code=status.HTTP_200_OK,
    summary="Сообщить о блокировке домена",
    description="Публикует задачу блокировки в RabbitMQ и выдает заведению новый URL для плеера.",
)
async def report_domain_ban(
    payload: ReportBanRequest,
    current_venue: Venue = Depends(get_current_player_venue),
) -> ReportBanResponse:
    domain_str = str(payload.url).rstrip("/")
    domain = await PlayerDomain.get_or_none(url=domain_str)

    if domain:
        domain.is_banned = True
        domain.is_active = False
        await domain.save(update_fields=["is_banned", "is_active", "updated_at"])

        await broker.publish(
            message={"domain_id": str(domain.id)},
            queue="domain_ban_queue",
        )

    new_domain = await DomainService.assign_domain_to_venue(current_venue)

    new_token = DomainService.generate_player_token(current_venue)
    new_url = f"{new_domain.url}/player?token={new_token}"

    return ReportBanResponse(new_url=new_url)
