from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.database import get_db
from backend.repositories.players import PlayerRepository
from backend.services.players import PlayerService

router = APIRouter(prefix="/players", tags=["Player Analytics"])

def get_player_service(db: AsyncSession = Depends(get_db)) -> PlayerService:
    return PlayerService(PlayerRepository(db))

@router.get("/{player_name}/profile", tags=["Player Analytics"])
async def get_individual_player_profile(
        player_name: str,
        season: str = Query("2025/2026"),
        service: PlayerService = Depends(get_player_service)
):
    return await service.get_player_profile(player_name, season)