# run_parser.py
import glob
import os
import logging
from dotenv import load_dotenv
import psycopg
from report_parser import DataVolleyParser

# Load credentials from .env file
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

DB_CONN_STRING = f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("parser_errors.log", mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def get_or_create_team(cur, team_name: str) -> int:
    """
    Looks up a team by name. Returns its ID.
    If the team doesn't exist, inserts it and returns the newly generated ID.
    """
    # 1. Check if the team already exists
    cur.execute("SELECT id FROM teams WHERE team_name = %s;", (team_name,))
    result = cur.fetchone()
    if result:
        return result[0]

    # 2. If it doesn't exist, insert it and get the identity ID back
    cur.execute("INSERT INTO teams (team_name) VALUES (%s) RETURNING id;", (team_name,))
    return cur.fetchone()[0]


def main():
    saved_files = glob.glob("match_reports/match_*.pdf")
    logging.info(f"Beginning database ingestion on {len(saved_files)} files...")

    # Health Check: Validate database connection before starting heavy parsing
    try:
        with psycopg.connect(DB_CONN_STRING) as conn:
            pass
    except psycopg.OperationalError:
        logging.critical("Cannot connect to PostgreSQL. Did you forget to run setup_db.py?")
        return

    # Process files
    with psycopg.connect(DB_CONN_STRING) as conn:
        with conn.cursor() as cur:

            for file_path in saved_files:
                file_name = os.path.basename(file_path)
                logging.info(f"Processing: {file_name}")

                try:
                    parser = DataVolleyParser(file_path)
                    report = parser.build_report()

                    # STEP 1: Resolve Home and Away Team IDs
                    home_team_id = get_or_create_team(cur, report.home_team)
                    away_team_id = get_or_create_team(cur, report.away_team)

                    # STEP 2: Insert Match metadata using the resolved Team IDs
                    cur.execute("""
                        INSERT INTO matches (file_origin, match_date, season, home_team_id, away_team_id)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (file_origin) DO NOTHING
                        RETURNING id;
                    """, (report.file_name, report.match_date, report.season, home_team_id, away_team_id))

                    match_result = cur.fetchone()

                    if match_result is None:
                        logging.warning(f"Skipped {file_name} (File already exists in database).")
                        continue

                    match_id = match_result[0]

                    # STEP 3: Insert Players
                    for player in report.players:
                        # Resolve the ID for the team the player was representing in this specific match
                        player_team_id = get_or_create_team(cur, player.team_played_for)

                        cur.execute("""
                            INSERT INTO player_match_stats 
                            (match_id, jersey, player_name, team_played_for_id, is_libero, total_receptions, reception_errors)
                            VALUES (%s, %s, %s, %s, %s, %s, %s);
                        """, (
                            match_id,
                            player.jersey,
                            player.name,
                            player_team_id,
                            player.is_libero,
                            player.total_receptions,
                            player.reception_errors
                        ))

                    # Safely commit all changes for this single PDF match report
                    conn.commit()
                    logging.info(f"Successfully ingested match metadata and {len(report.players)} player records from {file_name}.")

                except Exception as e:
                    # If anything crashes mid-file, wipe out the temporary inserts for this file
                    conn.rollback()
                    logging.error(f"CRASH OCCURRED while processing {file_name}. Rolling back transaction.", exc_info=True)

    logging.info("Database ingestion pipeline complete.")

if __name__ == "__main__":
    main()