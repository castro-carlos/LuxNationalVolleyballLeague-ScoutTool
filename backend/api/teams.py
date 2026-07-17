from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.db.database import get_db
from backend.schemas.teams import TeamResponse
from backend.schemas.players import PlayerReceptionErrorReport
from backend.repositories.teams import TeamRepository
from backend.services.teams import TeamService

router = APIRouter(
    prefix="/teams",
    tags=["Teams Management"]
)

# Tiny dependency injection wrapper to set up our architectural layers
def get_team_service(db: AsyncSession = Depends(get_db)) -> TeamService:
    repo = TeamRepository(db)
    return TeamService(repo)

@router.get("", response_model=List[TeamResponse], tags=["Teams Management"])
async def get_all_teams(service: TeamService = Depends(get_team_service)):
    return await service.list_teams()

@router.get("/{team_id}/reception-scout", response_model=List[PlayerReceptionErrorReport], tags=["Scouting & Analytics"])
async def get_team_reception_error_scout_report(
        team_id: int,
        season: str = Query("2025/2026", description="Season format: YYYY/YYYY"),
        min_receptions: int = Query(10, description="Minimum total receptions required to be listed"),
        service: TeamService = Depends(get_team_service)
):
    return await service.get_reception_scout_report(team_id, season, min_receptions)