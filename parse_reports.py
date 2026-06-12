import glob
import os
import re
import pymupdf
from collections import defaultdict
from datetime import datetime
import traceback
import pandas as pd


def extract_rows(page):

    words = page.get_text("words")

    rows = defaultdict(list)

    for x0, y0, x1, y1, text, block, line, word in words:

        y = round(y0, 1)

        rows[y].append((x0, text))

    rebuilt_rows = []

    for y in sorted(rows):

        row = " ".join(
            text
            for x, text in sorted(rows[y])
        )

        rebuilt_rows.append(row.strip())

    return rebuilt_rows


def clean_stat(token):
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

def extract_match_date(rows):

    for row in rows:

        if row.startswith("Date "):

            match = re.search(
                r"\b\d{2}/\d{2}/\d{4}\b",
                row
            )

            if match:
                return datetime.strptime(
                    match.group(),
                    "%d/%m/%Y"
                ).date()

    return None

def extract_teams(rows):

    idx = rows.index("Match report")

    home = rows[idx - 1]
    away = rows[idx + 1]

    home = re.sub(r"\s+\d+$", "", home)
    away = re.sub(r"\s+\d+$", "", away)

    return home, away

def extract_player_rows(rows, team):
    player_rows = []

    inside_players = False
    header_skipped = False
    for row in rows:

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
            player_rows.append(row)

    return player_rows

def extract_reception_data(player_row):
    tokens = player_row.strip().split()
    if not tokens:
        return None
    # 1. Use your name logic to find out where the player prefix ends
    is_libero = len(tokens) > 1 and tokens[1] == 'L'
    start_idx = 2 if is_libero else 1

    name_tokens_count = 0
    for token in tokens[start_idx:]:
        # Stop counting when we hit a stat placeholder (.) or any number/symbol
        if token == '.' or any(char.isdigit() for char in token) or token in ['(', ')']:
            break
        name_tokens_count += 1

    prefix_length = start_idx + name_tokens_count
    stat_tokens = tokens[prefix_length:]

    total_receptions = clean_stat(stat_tokens[7])
    reception_errors = clean_stat(stat_tokens[8])

    return (total_receptions, reception_errors)

def extract_player_name_data(player_row):
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

if __name__ == "__main__":
    saved_files = glob.glob("match_reports/match_*.pdf")
    all_player_stats = []

    print(f"Beginning extraction on {len(saved_files)} files...\n")

    for file_path in saved_files:
        print(f"Processing: {os.path.basename(file_path)}")

        try:
            doc = pymupdf.open(file_path)
            # Extract rows from the first page
            rows = extract_rows(doc[0])

            # --- CONNECTING YOUR FUNCTIONS ---
            match_date = extract_match_date(rows)
            home_team, away_team = extract_teams(rows)
            home_player_rows = extract_player_rows(rows, home_team)
            away_player_rows = extract_player_rows(rows, away_team)

            print(f"  Date: {match_date} | Teams: {home_team} vs {away_team}")
            print(f"  Found {len(home_player_rows)} home player rows.")
            print(f" Found {len(away_player_rows)} away player rows")
            print(home_player_rows)
            print(away_player_rows)

            # Build list of dictionaries
            for home_player_row in home_player_rows:
                player_total_receptions, player_reception_errors = extract_reception_data(home_player_row)
                player_name = extract_player_name_data(home_player_row)

                player_row_dict = {
                    "Match_Date": match_date,
                    "Team": home_team,
                    "Player_Name": player_name,
                    "Total_Receptions": player_total_receptions,
                    "Reception_Errors": player_reception_errors,
                }

                all_player_stats.append(player_row_dict)

            for away_player_row in away_player_rows:
                player_total_receptions, player_reception_errors = extract_reception_data(away_player_row)
                player_name = extract_player_name_data(away_player_row)

                player_row_dict = {
                    "Match_Date": match_date,
                    "Team": away_team,
                    "Player_Name": player_name,
                    "Total_Receptions": player_total_receptions,
                    "Reception_Errors": player_reception_errors,
                }

                all_player_stats.append(player_row_dict)

            print(all_player_stats)
            print("wow")
        except Exception as e:
            print(f"  Error processing {os.path.basename(file_path)}: {e}")
            traceback.print_exc()

    print("\nProcessing finished.")