from schemas.teams import TeamResponse

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc, case, Float
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from db.models import Team, Match, PlayerMatchStat
from schemas.players import PlayerReceptionErrorReport

router = APIRouter(
    prefix="/teams",
    tags=["Teams Management"]
)

@router.get("", response_model=List[TeamResponse], tags=["Teams Management"])
def get_all_teams(db: Session = Depends(get_db)):
    try:
        stmt = select(Team).order_by(Team.team_name)
        return db.scalars(stmt).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teams/{team_id}/reception-scout", response_model=List[PlayerReceptionErrorReport], tags=["Scouting & Analytics"])
def get_team_reception_error_scout_report(
        team_id: int,
        season: str = Query(..., description="Season format: YYYY/YYYY"),
        db: Session = Depends(get_db)
):
    # 1. Verify that the target team exists
    team = db.scalar(select(Team).where(Team.id == team_id))
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # 2. CTE: Determine the "Actual Team" for every single player this season
    # Row number ranks every player's matches from newest to oldest based on match_date
    window_expr = func.row_number().over(
        partition_by=PlayerMatchStat.player_name,
        order_by=desc(Match.match_date)
    ).label("match_rank")

    latest_player_team_cte = (
        select(
            PlayerMatchStat.player_name,
            PlayerMatchStat.team_played_for_id,
            window_expr
        )
        .join(Match, PlayerMatchStat.match_id == Match.id)
        .where(Match.season == season)
        .cte("latest_player_team_cte")
    )

    # 3. Subquery: Filter the CTE to isolate players whose LATEST match was with our target team
    current_team_players_subq = (
        select(latest_player_team_cte.c.player_name)
        .where(
            latest_player_team_cte.c.match_rank == 1,
            latest_player_team_cte.c.team_played_for_id == team_id
        )
        .subquery()
    )

    # 4. Main Query: Aggregate the entire season stats specifically for those active players
    # Safe division logic handles cases where a player has 0 total receptions
    error_percentage_expr = case(
        (func.sum(PlayerMatchStat.total_receptions) == 0, 0.0),
        else_=(
                      func.cast(func.sum(PlayerMatchStat.reception_errors), Float) /
                      func.cast(func.sum(PlayerMatchStat.total_receptions), Float)
              ) * 100.0
    ).label("error_percentage")

    stats_stmt = (
        select(
            PlayerMatchStat.player_name,
            func.sum(PlayerMatchStat.total_receptions).label("total_receptions"),
            func.sum(PlayerMatchStat.reception_errors).label("reception_errors"),
            error_percentage_expr
        )
        .join(Match, PlayerMatchStat.match_id == Match.id)
        .where(
            Match.season == season,
            PlayerMatchStat.player_name.in_(select(current_team_players_subq))
        )
        .group_by(PlayerMatchStat.player_name)
        .order_by(desc("error_percentage")) # Ascending order: Best performance up top
    )

    # 5. Execute transaction and return the dataset mappings
    results = db.execute(stats_stmt).mappings().all()
    return results