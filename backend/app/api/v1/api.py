from fastapi import APIRouter

from app.modules.auth.router import router as auth_router
from app.modules.music.router import router as music_router
from app.modules.player.router import router as player_router
from app.modules.soundcloud.router import router as soundcloud_router
from app.modules.venues.router import router as venues_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(venues_router, prefix="/venues", tags=["Venues"])
api_router.include_router(music_router, prefix="/music", tags=["Music"])
api_router.include_router(soundcloud_router, prefix="/storage", tags=["Storage"])
api_router.include_router(player_router, prefix="/player", tags=["Player"])
