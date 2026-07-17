from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, case, Float
from backend.db.models import Team, Match, PlayerMatchStat

class TeamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _get_current_roster_subquery(self, team_id: int, season: str):
        """
        Returns a subquery of player names whose LATEST match
        this season was for the target team.
        """
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

        return (
            select(latest_player_team_cte.c.player_name)
            .where(
                latest_player_team_cte.c.match_rank == 1,
                latest_player_team_cte.c.team_played_for_id == team_id
            )
            .subquery()
        )

    async def get_all(self):
        stmt = select(Team).order_by(Team.team_name)
        result = await self.db.scalars(stmt)
        return result.all()

    async def get_by_id(self, team_id: int):
        return await self.db.scalar(select(Team).where(Team.id == team_id))

    async def get_season_reception_stats(self, team_id: int, season: str, min_receptions: int):
        roster_subq = self._get_current_roster_subquery(team_id, season)

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
                PlayerMatchStat.player_name.in_(roster_subq.select())
            )
            .group_by(PlayerMatchStat.player_name)
            .having(func.sum(PlayerMatchStat.total_receptions) >= min_receptions)
            .order_by(desc("error_percentage"))
        )

        raw_results = await self.db.execute(stats_stmt)
        return raw_results.mappings().all()

    async def get_season_attack_volume_stats(self, team_id: int, season: str, min_attacks: int):
        roster_subq = self._get_current_roster_subquery(team_id, season)

        # Efficiency Formula: (Kills - Errors - Blocked) / Total Attacks * 100
        efficiency_expr = case(
            (func.sum(PlayerMatchStat.attack_total) == 0, 0.0),
            else_=(
                          func.cast(
                              func.sum(PlayerMatchStat.attack_kills) -
                              func.sum(PlayerMatchStat.attack_errors) -
                              func.sum(PlayerMatchStat.attack_blocked), Float
                          ) / func.cast(func.sum(PlayerMatchStat.attack_total), Float)
                  ) * 100.0
        ).label("attack_efficiency")

        stats_stmt = (
            select(
                PlayerMatchStat.player_name,
                func.sum(PlayerMatchStat.attack_total).label("total_attacks"),
                func.sum(PlayerMatchStat.attack_kills).label("attack_kills"),
                func.sum(PlayerMatchStat.attack_errors).label("attack_errors"),
                func.sum(PlayerMatchStat.attack_blocked).label("attack_blocked"),
                efficiency_expr
            )
            .join(Match, PlayerMatchStat.match_id == Match.id)
            .where(
                Match.season == season,
                PlayerMatchStat.player_name.in_(roster_subq.select())
            )
            .group_by(PlayerMatchStat.player_name)
            .having(func.sum(PlayerMatchStat.attack_total) >= min_attacks)
            .order_by(desc("total_attacks"))  # Order by heaviest offensive volume up top
        )

        raw_results = await self.db.execute(stats_stmt)
        return raw_results.mappings().all()

    async def get_season_service_stats(self, team_id: int, season: str, min_serves: int):
        roster_subq = self._get_current_roster_subquery(team_id, season)

        # Efficiency Formula: Aces / Total Serves * 100
        efficiency_expr = case(
            (func.sum(PlayerMatchStat.service_total) == 0, 0.0),
            else_=(
                          func.cast(
                              func.sum(PlayerMatchStat.service_aces)
                             , Float
                          ) / func.cast(func.sum(PlayerMatchStat.service_total), Float)
                  ) * 100.0
        ).label("service_efficiency")

        # Error Formula: Misses / Total Serves * 100
        error_rate = case(
            (func.sum(PlayerMatchStat.service_total) == 0, 0.0),
            else_=(
                          func.cast(
                              func.sum(PlayerMatchStat.service_errors)
                              , Float
                          ) / func.cast(func.sum(PlayerMatchStat.service_total), Float)
                  ) * 100.0
        ).label("service_error_rate")

        stats_stmt = (
            select(
                PlayerMatchStat.player_name,
                func.sum(PlayerMatchStat.service_total).label("total_serves"),
                func.sum(PlayerMatchStat.service_aces).label("aces"),
                func.sum(PlayerMatchStat.service_errors).label("error_serves"),
                efficiency_expr,
                error_rate
            )
            .join(Match, PlayerMatchStat.match_id == Match.id)
            .where(
                Match.season == season,
                PlayerMatchStat.player_name.in_(roster_subq.select())
            )
            .group_by(PlayerMatchStat.player_name)
            .having(func.sum(PlayerMatchStat.service_total) >= min_serves)
            .order_by(desc("total_serves"))  # Order by most serves up top
        )

        raw_results = await self.db.execute(stats_stmt)
        return raw_results.mappings().all()