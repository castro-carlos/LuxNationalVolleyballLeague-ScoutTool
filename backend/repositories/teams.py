from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, case, Float
from backend.db.models import Team, Match, PlayerMatchStat

class TeamRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        stmt = select(Team).order_by(Team.team_name)
        result = await self.db.scalars(stmt)
        return result.all()

    async def get_by_id(self, team_id: int):
        return await self.db.scalar(select(Team).where(Team.id == team_id))

    async def get_season_reception_stats(self, team_id: int, season: str, min_receptions: int):
        # 1. CTE: Determine the "Actual Team" for every player this season via latest match
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

        # 2. Subquery: Isolate players whose LATEST match was with our target team
        current_team_players_subq = (
            select(latest_player_team_cte.c.player_name)
            .where(
                latest_player_team_cte.c.match_rank == 1,
                latest_player_team_cte.c.team_played_for_id == team_id
            )
            .subquery()
        )

        # 3. Main Query: Calculate mathematical error aggregates
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
                PlayerMatchStat.player_name.in_(current_team_players_subq.select())
            )
            .group_by(PlayerMatchStat.player_name)
            .having(func.sum(PlayerMatchStat.total_receptions) >= min_receptions)
            .order_by(desc("error_percentage"))
        )

        raw_results = await self.db.execute(stats_stmt)
        return raw_results.mappings().all()

    async def get_season_attack_volume_stats(self, team_id: int, season: str, min_attacks: int):
        """
        Aggregates season attack volume and efficiency metrics for the current roster.
        """
        # 1. CTE: Determine the "Actual Team" for every player this season via latest match
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

        # 2. Subquery: Isolate players whose LATEST match was with our target team
        current_team_players_subq = (
            select(latest_player_team_cte.c.player_name)
            .where(
                latest_player_team_cte.c.match_rank == 1,
                latest_player_team_cte.c.team_played_for_id == team_id
            )
            .subquery()
        )

        # 3. Main Query: Calculate attack volume and hitting efficiency
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
                PlayerMatchStat.player_name.in_(current_team_players_subq.select())
            )
            .group_by(PlayerMatchStat.player_name)
            .having(func.sum(PlayerMatchStat.attack_total) >= min_attacks)
            .order_by(desc("total_attacks"))  # Order by heaviest offensive volume up top
        )

        raw_results = await self.db.execute(stats_stmt)
        return raw_results.mappings().all()