import re
import pymupdf
from collections import defaultdict
from datetime import datetime
from models import MatchReport, PlayerMatchStats
from typing import List

class DataVolleyParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.doc = pymupdf.open(file_path)
        self.rows = self._extract_rows(self.doc[0])

    def _extract_rows(self, page) -> list:
        # Your original PDF word placement rebuilt here
        words = page.get_text("words")
        rows = defaultdict(list)
        for x0, y0, x1, y1, text, block, line, word in words:
            y = round(y0, 1)
            rows[y].append((x0, text))

        rebuilt_rows = []
        for y in sorted(rows):
            row = " ".join(text for x, text in sorted(rows[y]))
            rebuilt_rows.append(row.strip())
        return rebuilt_rows

    def parse_date(self) -> datetime.date:
        for row in self.rows:
            if row.startswith("Date "):
                match = re.search(r"\b\d{2}/\d{2}/\d{4}\b", row)
                if match:
                    return datetime.strptime(match.group(), "%d/%m/%Y").date()
        return None

    def parse_teams(self) -> tuple:
        idx = self.rows.index("Match report")
        home = re.sub(r"\s+\d+$", "", self.rows[idx - 1])
        away = re.sub(r"\s+\d+$", "", self.rows[idx + 1])
        return home, away

    def clean_stat(self, token):
        # Remove any hidden spaces or newlines
        token = token.strip() if token else ""
    
        # If it's just a dot or completely empty, normalize it to "0"
        if token == "." or token == "":
            return 0
    
        try:
            cleaned = token.replace('%', '').strip()
            return int(cleaned)
        except ValueError:
            return 0

    def parse_season(self):
        return "2025/2026"

    def extract_player_jersey_data(self, player_row):
        tokens = player_row.strip().split()
        if not tokens:
            return None
        return int(tokens[0])

    def extract_player_name_data(self, player_row):
        tokens = player_row.strip().split()
        if not tokens:
            return None

        is_libero = False
        if len(tokens) > 1:
            if tokens[1] == 'L':
                is_libero = True

        start_idx = 2 if is_libero else 1
        name_tokens = []
        for token in tokens[start_idx:]:
            if token == '.' or any(char.isdigit() for char in token):
                break
            name_tokens.append(token)
        player_name = " ".join(name_tokens)
        return player_name

    def extract_player_reception_data(self, player_row):
        tokens = player_row.strip().split()
        if not tokens:
            return None
        # 1. Use your name logic to find out where the player prefix ends
        is_libero = self.extract_player_libero_data(player_row)
        start_idx = 2 if is_libero else 1
    
        name_tokens_count = 0
        for token in tokens[start_idx:]:
            # Stop counting when we hit a stat placeholder (.) or any number/symbol
            if token == '.' or any(char.isdigit() for char in token) or token in ['(', ')']:
                break
            name_tokens_count += 1
    
        prefix_length = start_idx + name_tokens_count
        stat_tokens = tokens[prefix_length:]
    
        total_receptions = self.clean_stat(stat_tokens[7])
        reception_errors = self.clean_stat(stat_tokens[8])
    
        return (total_receptions, reception_errors)

    def extract_player_libero_data(self, player_row):
        tokens = player_row.strip().split()
        if len(tokens) < 2:
            return False
        return tokens[1] == 'L'

    def parse_players(self, team) -> List[PlayerMatchStats]:
        player_objects = []

        inside_players = False
        header_skipped = False
        for row in self.rows:

            if row == team:
                inside_players = True
                header_skipped = False
                continue

            if inside_players and row.startswith("Players total"):
                break

            if not inside_players:
                continue

            if not header_skipped:
                header_skipped = True
                continue

            if re.match(r"^\d+\s+", row):
                player_jersey = self.extract_player_jersey_data(row)
                player_name = self.extract_player_name_data(row)
                is_player_libero = self.extract_player_libero_data(row)
                player_total_receptions, player_reception_errors = self.extract_player_reception_data(row)

                player_objects.append(PlayerMatchStats(
                    jersey=player_jersey,
                    name=player_name,
                    team_played_for=team,
                    is_libero=is_player_libero,
                    total_receptions=player_total_receptions,
                    reception_errors=player_reception_errors
                ))

        return player_objects

    def build_report(self) -> MatchReport:
        """Assembles all components into a complete MatchReport object."""
        home, away = self.parse_teams()

        home_players = self.parse_players(home)
        away_players = self.parse_players(away)
        all_players = home_players + away_players

        return MatchReport(
            file_name=self.file_path,
            match_date=self.parse_date(),
            season = self.parse_season(),
            home_team=home,
            away_team=away,
            players=all_players
        )