# backend/repositories/players.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, Float, case
from backend.db.models import PlayerMatchStat, Match

class PlayerRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_player_match_history(self, player_name: str, season: str):
        """
        Retrieves a game-by-game performance log for a single player.
        """
        stmt = (
            select(
                Match.match_date,
                Match.home_team,
                Match.away_team,
                PlayerMatchStat.points_total,
                PlayerMatchStat.attack_kills,
                PlayerMatchStat.service_aces,
                PlayerMatchStat.block_points
            )
            .join(Match, PlayerMatchStat.match_id == Match.id)
            .where(
                func.lower(PlayerMatchStat.player_name) == player_name.lower(),
                Match.season == season
            )
            .order_by(desc(Match.match_date))
        )

        raw_results = await self.db.execute(stmt)
        return raw_results.mappings().all()