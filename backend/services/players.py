from fastapi import HTTPException
from backend.repositories.players import PlayerRepository

class PlayerService:
    def __init__(self, repo: PlayerRepository):
        self.repo = repo

    async def get_player_profile(self, player_name: str, season: str):
        matches = await self.repo.get_player_match_history(player_name, season)
        if not matches:
            raise HTTPException(status_code=404, detail=f"No stats found for player '{player_name}'")

        return {
            "player_name": player_name,
            "season": season,
            "match_log": matches
        }