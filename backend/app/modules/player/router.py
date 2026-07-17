import asyncio
import logging
from uuid import UUID, uuid4

from app.api.dependencies import get_current_player_venue, get_ws_player_venue
from app.broker.publisher import EventPublisher
from app.core.redis import redis_cache
from app.modules.auth.schemas import MessageResponse
from app.modules.music.models import Playlist, PlaylistTrack
from app.modules.music.schemas import (
    QueueItem,
    TrackSourceType,
)
from app.modules.music.services import MusicStorageService, QueueService
from app.modules.player.schemas import (
    AddPlaylistTrackRequest,
    AddTrackRequest,
    CreatePlaylistRequest,
    LiveQueueResponse,
    PlaylistDetailsResponse,
    PlaylistResponse,
    ReorderQueueRequest,
)
from app.modules.player.services import PlayerConnectionService, PlayerWebSocketManager
from app.modules.venues.models import Venue
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from pydantic import UUID4
from tortoise.transactions import in_transaction

logger = logging.getLogger(__name__)

router = APIRouter()

# ==========================================
# УПРАВЛЕНИЕ ПЛЕЙЛИСТАМИ (DJ-пульт бармена)
# Защищено токеном плеера
# ==========================================


@router.get(
    "/playlists",
    response_model=list[PlaylistResponse],
    summary="Получить список всех плейлистов",
    description="Возвращает список плейлистов для UI диджей-пульта",
)
async def get_playlists(
    venue: Venue = Depends(get_current_player_venue),
) -> list[PlaylistResponse]:
    playlists = await MusicStorageService.get_venue_playlists(venue_id=venue.id)
    return playlists  # type: ignore[return-value]


@router.get(
    "/playlists/{playlist_id}",
    response_model=PlaylistDetailsResponse,
    summary="Получить детали плейлиста (со списком треков)",
)
async def get_playlist_details(
    playlist_id: UUID,
    venue: Venue = Depends(get_current_player_venue),
) -> PlaylistDetailsResponse:
    playlist = await Playlist.get_or_none(id=playlist_id, venue_id=venue.id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Плейлист не найден")

    tracks = await MusicStorageService.get_playlist_tracks(playlist_id=playlist_id)

    return PlaylistDetailsResponse(
        id=playlist.id,
        name=playlist.name,
        is_active=playlist.is_active,
        tracks=tracks,  # type: ignore[arg-type]
    )


@router.post(
    "/playlists",
    response_model=MessageResponse,
    summary="Создать новый плейлист",
)
async def create_playlist(
    request: CreatePlaylistRequest,
    venue: Venue = Depends(get_current_player_venue),
) -> MessageResponse:
    await Playlist.create(venue_id=venue.id, name=request.name)
    return MessageResponse(message=f"Плейлист '{request.name}' успешно создан")


@router.delete(
    "/playlists/{playlist_id}",
    response_model=MessageResponse,
    summary="Удалить плейлист",
)
async def delete_playlist(
    playlist_id: UUID,
    venue: Venue = Depends(get_current_player_venue),
) -> MessageResponse:
    playlist = await Playlist.get_or_none(id=playlist_id, venue_id=venue.id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Плейлист не найден")

    await playlist.delete()
    return MessageResponse(message="Плейлист удален")


@router.post(
    "/playlists/{playlist_id}/tracks",
    response_model=MessageResponse,
    summary="Добавление трека в плейлист",
)
async def add_track_to_playlist(
    playlist_id: UUID,
    request: AddPlaylistTrackRequest,
    venue: Venue = Depends(get_current_player_venue),
) -> MessageResponse:
    playlist = await Playlist.get_or_none(id=playlist_id, venue_id=venue.id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Плейлист не найден.")

    exists = await PlaylistTrack.filter(
        playlist_id=playlist_id, track_id=str(request.track_id)
    ).exists()

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Этот трек уже присутствует в данном плейлисте.",
        )

    last_track = await PlaylistTrack.filter(playlist_id=playlist_id).order_by("-sort_order").first()
    next_order = last_track.sort_order + 1 if last_track else 1

    await PlaylistTrack.create(
        playlist_id=playlist_id,
        track_id=str(request.track_id),
        track_url=request.track_url,
        title=request.title,
        artist=request.artist,
        artwork_url=request.artwork_url,
        duration_ms=request.duration_ms,
        sort_order=next_order,
    )

    return MessageResponse(message="Трек успешно добавлен в плейлист")


@router.delete(
    "/playlists/{playlist_id}/tracks/{track_id}",
    response_model=MessageResponse,
    summary="Удаление трека из плейлиста",
)
async def remove_track_from_playlist(
    playlist_id: UUID,
    track_id: int,
    venue: Venue = Depends(get_current_player_venue),
) -> MessageResponse:
    playlist = await Playlist.get_or_none(id=playlist_id, venue_id=venue.id)
    if not playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Плейлист не найден.")

    track = await PlaylistTrack.get_or_none(playlist_id=playlist_id, track_id=str(track_id))
    if not track:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Трек не найден в указанном плейлисте."
        )

    await track.delete()
    return MessageResponse(message="Трек удален из плейлиста.")


# ==========================================
# REST API ПЛЕЕРА (Управление очередью)
# Защищено HTTPBearer зависимостью get_current_player_venue
# ==========================================


@router.get(
    "/state",
    response_model=LiveQueueResponse,
    summary="Получить текущее состояние плеера",
    description="""Вызывается фронтендом плеера при первой загрузке
    страницы для восстановления состояния.""",
)
async def get_player_state(venue: Venue = Depends(get_current_player_venue)) -> LiveQueueResponse:
    currently_playing = await QueueService.get_currently_playing(venue.id)
    items = await QueueService.get_queue(venue.id)
    return LiveQueueResponse(currently_playing=currently_playing, items=items)


@router.post(
    "/queue/playlist/{playlist_id}",
    response_model=MessageResponse,
    summary="Запуск фонового плейлиста",
)
async def add_playlist_to_queue(
    playlist_id: UUID4,
    venue: Venue = Depends(get_current_player_venue),
) -> MessageResponse:
    tracks = await MusicStorageService.get_playlist_tracks(playlist_id=playlist_id)
    if not tracks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Плейлист не найден или пуст."
        )

    async with in_transaction():
        await Playlist.filter(venue_id=venue.id).update(is_active=False)
        await Playlist.filter(id=playlist_id, venue_id=venue.id).update(is_active=True)

    queue_items = [
        QueueItem(
            queue_id=str(uuid4()),
            track_id=int(t.track_id),
            track_url=t.track_url,
            title=t.title,
            artist=t.artist,
            artwork_url=t.artwork_url,
            duration_ms=0,
            source_type=TrackSourceType.BACKGROUND,
            order_id=None,
        )
        for t in tracks
    ]

    await QueueService.add_playlist(venue_id=venue.id, items=queue_items)
    return MessageResponse(message="Плейлист запущен")


@router.post(
    "/queue/track",
    response_model=QueueItem,
    summary="Бармен добавляет одиночный трек",
)
async def add_single_track(
    request: AddTrackRequest,
    venue: Venue = Depends(get_current_player_venue),
) -> QueueItem:
    track_data = request.model_dump()
    if request.source_type == TrackSourceType.BACKGROUND:
        track_data["order_id"] = None

    return await QueueService.add_track(venue_id=venue.id, track_data=track_data)


@router.post(
    "/queue/track/next",
    response_model=QueueItem,
    summary="Бармен добавляет трек 'Играть следующим'",
)
async def add_track_next(
    request: AddTrackRequest,
    venue: Venue = Depends(get_current_player_venue),
) -> QueueItem:
    track_data = request.model_dump()
    if request.source_type == TrackSourceType.BACKGROUND:
        track_data["order_id"] = None

    return await QueueService.add_track_next(venue_id=venue.id, track_data=track_data)


@router.delete(
    "/queue/track/{queue_id}",
    response_model=MessageResponse,
    summary="Удаление трека из очереди",
)
async def remove_track_from_queue(
    queue_id: str,
    venue: Venue = Depends(get_current_player_venue),
) -> MessageResponse:
    current_queue = await QueueService.get_queue(venue_id=venue.id)

    track_to_remove = next((item for item in current_queue if item.queue_id == queue_id), None)
    if not track_to_remove:
        raise HTTPException(status_code=404, detail="Трек не найден в очереди.")

    updated_queue = [item for item in current_queue if item.queue_id != queue_id]
    await QueueService._save_queue(venue_id=venue.id, items=updated_queue)
    return MessageResponse(message="Трек удален")


@router.put(
    "/queue/reorder",
    response_model=MessageResponse,
    summary="Изменение порядка (Drag-and-Drop)",
)
async def reorder_queue(
    request: ReorderQueueRequest,
    venue: Venue = Depends(get_current_player_venue),
) -> MessageResponse:
    await QueueService.apply_drag_and_drop(
        venue_id=venue.id, new_order_ids=request.new_order_queue_ids
    )
    return MessageResponse(message="Порядок обновлен")


@router.post(
    "/queue/skip",
    response_model=MessageResponse,
    summary="Пропуск текущего трека (Next / Skip)",
)
async def skip_current_track(venue: Venue = Depends(get_current_player_venue)) -> MessageResponse:
    playing_track = await QueueService.get_currently_playing(venue_id=venue.id)
    if not playing_track:
        return MessageResponse(message="Нет играющего трека для пропуска")

    if playing_track.order_id:
        await EventPublisher.publish_order_played(
            order_id=playing_track.order_id,
            track_id=playing_track.track_id,
            was_skipped=True,
        )

    await QueueService.trigger_playback(venue_id=venue.id)
    return MessageResponse(message="Трек пропущен")


# ==========================================
# WEBSOCKET ПЛЕЕРА (Реактивность)
# Защищено Query-зависимостью get_ws_player_venue
# ==========================================


@router.websocket("/ws")
async def player_websocket_endpoint(
    websocket: WebSocket,
    venue: Venue = Depends(get_ws_player_venue),
) -> None:
    """
    Эндпоинт для подключения плеера заведения.
    Поддерживает множественные коннекты.
    """
    session_id = await PlayerConnectionService.register_connection(venue.id)
    await PlayerWebSocketManager.connect(venue.id, websocket)

    try:
        while True:
            data = await asyncio.wait_for(websocket.receive_json(), timeout=45.0)

            is_valid = await PlayerConnectionService.is_session_valid(venue.id, session_id)
            if not is_valid:
                logger.info(f"Session {session_id} for venue {venue.id} is invalid. Closing WS.")
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                break

            msg_type = data.get("type")

            if msg_type == "PING":
                await websocket.send_json({"type": "PONG"})

            elif msg_type == "TRACK_ENDED":
                track_id = data.get("track_id")
                order_id_str = data.get("order_id")

                lock_key = f"venue:{venue.id}:track_ended_lock"
                acquired = await redis_cache.safe_client.set(lock_key, "locked", ex=3, nx=True)

                if not acquired:
                    logger.debug(
                        f"Skipping duplicate TRACK_ENDED from venue {venue.id} (debounce lock)"
                    )
                    continue

                if order_id_str:
                    try:
                        await EventPublisher.publish_order_played(
                            order_id=UUID(order_id_str),
                            track_id=int(track_id) if track_id else 0,
                            was_skipped=False,
                        )
                    except (ValueError, TypeError) as e:
                        logger.error(f"Failed to parse order_id from TRACK_ENDED event: {e}")

                await QueueService.trigger_playback(venue.id)

    except TimeoutError:
        logger.warning(f"WebSocket timeout for venue {venue.id} (No PING received).")
    except WebSocketDisconnect:
        logger.info(f"WebSocket cleanly disconnected for venue {venue.id} (session: {session_id}).")
    except Exception as e:
        logger.error(f"WebSocket unexpected error for venue {venue.id}: {e}")
    finally:
        PlayerWebSocketManager.disconnect(venue.id, websocket)
        await PlayerConnectionService.handle_disconnect(venue.id, session_id)
