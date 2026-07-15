import re
import pymupdf
from collections import defaultdict
from datetime import datetime
from backend.pdf_parser.extractors.point import PointsExtractor
from backend.pdf_parser.extractors.block import BlockExtractor
from backend.pdf_parser.extractors.reception import ReceptionExtractor
from backend.pdf_parser.extractors.service import ServiceExtractor
from backend.pdf_parser.extractors.attack import AttackExtractor
from backend.pdf_parser.dtos import MatchReport, PlayerMatchStats
from typing import List


class CoordinatedString(str):
    def __new__(cls, value, words):
        obj = super().__new__(cls, value)
        obj.words = words  # Holds the sorted list of (x0, text) tuples
        return obj


class DataVolleyParser:

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.doc = pymupdf.open(file_path)
        self.rows = self._extract_rows(self.doc[0])


    def _extract_rows(self, page) -> list:
        words = page.get_text("words")
        rows = defaultdict(list)
        for x0, y0, x1, y1, text, block, line, word in words:
            y = round(y0, 1)
            rows[y].append((x0, text))

        rebuilt_rows = []
        for y in sorted(rows):
            # Sort the tokens horizontally from left to right
            sorted_words = sorted(rows[y], key=lambda item: item[0])
            row_text = " ".join(text for x, text in sorted_words).strip()

            # Wrap the string in our custom class to preserve the coordinates
            rebuilt_rows.append(CoordinatedString(row_text, sorted_words))
        return rebuilt_rows

    def parse_date(self) -> datetime.date:
        for row in self.rows:
            if row.startswith("Date "):
                match = re.search(r"\b\d{2}[/-]\d{2}[/-]\d{4}\b", row)
                if match:
                    date_str = match.group().replace("-", "/")
                    return datetime.strptime(date_str, "%d/%m/%Y").date()

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

    def derive_season(self, match_date) -> str:
        """
        Derives the season string (YYYY/YYYY) programmatically from the match date,
        bypassing human typos in the PDF header text.
        """
        if not match_date:
            return "Unknown Season"

        year = match_date.year
        month = match_date.month

        # Volleyball seasons typically start around September (Month 9)
        if month >= 9:
            start_year = year
            end_year = year + 1
        else:
            start_year = year - 1
            end_year = year

        return f"{start_year}/{end_year}"

    def extract_player_jersey_data(self, player_row) -> int:
        tokens = player_row.strip().split()
        if not tokens:
            return None
        return int(tokens[0])

    def extract_player_name_data(self, player_row) -> str:
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

    def extract_player_libero_data(self, player_row) -> bool:
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

                words = getattr(row, "words", [])

                tot_pts, bp_pts, plus_minus = PointsExtractor.extract(words, self.clean_stat)

                tot_rec, rec_err, pos_rec, exc_rec = ReceptionExtractor.extract(words, self.clean_stat)

                tot_srv, srv_err, srv_ace = ServiceExtractor.extract(words, self.clean_stat)

                tot_att, att_err, att_blk, att_kill = AttackExtractor.extract(words, self.clean_stat)

                blk_pts = BlockExtractor.extract(words, self.clean_stat)

                player_objects.append(PlayerMatchStats(
                    jersey=player_jersey,
                    name=player_name,
                    team_played_for=team,
                    is_libero=is_player_libero,

                    points_total=tot_pts,
                    points_break=bp_pts,
                    plus_minus=plus_minus,

                    service_total=tot_srv,
                    service_errors=srv_err,
                    service_aces=srv_ace,

                    total_receptions=tot_rec,
                    reception_errors=rec_err,
                    positive_receptions=pos_rec,
                    excellent_receptions=exc_rec,

                    attack_total=tot_att,
                    attack_errors=att_err,
                    attack_blocked=att_blk,
                    attack_kills=att_kill,

                    block_points=blk_pts
                ))

        return player_objects

    def build_report(self) -> MatchReport:
        """Assembles all components into a complete MatchReport object."""
        home, away = self.parse_teams()

        home_players = self.parse_players(home)
        away_players = self.parse_players(away)
        all_players = home_players + away_players
        match_date = self.parse_date()
        season_string = self.derive_season(match_date)

        return MatchReport(
            file_name=self.file_path,
            match_date=match_date,
            season = season_string,
            home_team=home,
            away_team=away,
            players=all_players
        )