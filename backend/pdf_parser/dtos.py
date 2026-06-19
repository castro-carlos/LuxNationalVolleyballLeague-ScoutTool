from dataclasses import dataclass
from datetime import date
from typing import List

@dataclass
class PlayerMatchStats:
    # Identifiers
    jersey: int
    name: str
    team_played_for: str  # e.g., "Volley Bartreng" (captures mid-season transfers cleanly)

    is_libero: bool = False
    total_receptions: int = 0
    reception_errors: int = 0



@dataclass
class MatchReport:
    file_name: str
    match_date: date
    season: str
    home_team: str
    away_team: str
    players: List[PlayerMatchStats]