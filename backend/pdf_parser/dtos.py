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

    points_total: int = 0
    points_break: int = 0
    plus_minus: int = 0

    total_receptions: int = 0
    reception_errors: int = 0
    positive_receptions: int = 0
    excellent_receptions: int = 0

    service_total: int = 0
    service_errors: int = 0
    service_aces: int = 0

    attack_total: int = 0
    attack_errors: int = 0
    attack_blocked: int = 0
    attack_kills: int = 0

    block_points: int = 0



@dataclass
class MatchReport:
    file_name: str
    match_date: date
    season: str
    home_team: str
    away_team: str
    players: List[PlayerMatchStats]