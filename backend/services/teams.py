from fastapi import HTTPException
from repositories.teams import TeamRepository

class TeamService:
    def __init__(self, repo: TeamRepository):
        self.repo = repo

    async def list_teams(self):
        return await self.repo.get_all()

    async def get_reception_scout_report(self, team_id: int, season: str, min_receptions: int):
        # Business Rule Verification: Ensure target team exists
        team = await self.repo.get_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return await self.repo.get_season_reception_stats(team_id, season, min_receptions)

    async def get_attack_volume_report(self, team_id: int, season: str, min_attacks: int):
        # Verify team exists
        team = await self.repo.get_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return await self.repo.get_season_attack_volume_stats(team_id, season, min_attacks)

    async def get_season_service_report(self, team_id: int, season: str, min_serves: int):
        # Verify team exists
        team = await self.repo.get_by_id(team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        return await self.repo.get_season_service_stats(team_id, season, min_serves)

