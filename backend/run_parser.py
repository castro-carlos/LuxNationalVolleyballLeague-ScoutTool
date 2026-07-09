import asyncio
import glob
import os
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # Use AsyncSession

from db.database import engine

from db.models import Team, Match, PlayerMatchStat

from pdf_parser.report_parser import DataVolleyParser

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

async def get_or_create_team(session, team_name: str) -> Team:
    """
    Looks up a team by name using SQLAlchemy ORM.
    Returns the Team object. If it doesn't exist, creates and flushes it.
    """
    stmt = select(Team).where(Team.team_name == team_name)
    result = await session.scalars(stmt)
    team = result.first()

    if not team:
        team = Team(team_name=team_name)
        session.add(team)
        await session.flush()

    return team


async def main():
    saved_files = glob.glob("match_reports/match_*.pdf")
    logging.info(f"Beginning database ingestion on {len(saved_files)} files...")

    # Health Check: Safely verify connection to the database container using the imported engine
    try:
        async with engine.connect() as conn:
            pass
    except Exception:
        logging.critical("Cannot connect to PostgreSQL via SQLAlchemy. Did you run setup_db.py?")
        return


    async with AsyncSession(bind=engine, expire_on_commit=False) as session:
        for file_path in saved_files:
            file_name = os.path.basename(file_path)
            logging.info(f"Processing: {file_name}")

            try:
                parser = DataVolleyParser(file_path)
                report = parser.build_report()

                # STEP 1: Handle skipping logic
                stmt = select(Match).where(Match.file_origin == report.file_name)
                result = await session.scalars(stmt)
                existing_match = result.first()

                if existing_match:
                    logging.warning(f"Skipped {file_name} (File already exists in database).")
                    continue

                # STEP 2: Resolve Home and Away Teams
                home_team = await get_or_create_team(session, report.home_team)
                away_team = await get_or_create_team(session, report.away_team)

                # STEP 3: Instantiate Match metadata object
                new_match = Match(
                    file_origin=report.file_name,
                    match_date=report.match_date,
                    season=report.season,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id
                )
                session.add(new_match)
                await session.flush()

                # STEP 4: Instantiate and associate Player stats
                for player in report.players:
                    player_team = await get_or_create_team(session, player.team_played_for)

                    new_stat = PlayerMatchStat(
                        match_id=new_match.id,
                        jersey=player.jersey,
                        player_name=player.name,
                        team_played_for_id=player_team.id,
                        is_libero=player.is_libero,
                        total_receptions=player.total_receptions,
                        reception_errors=player.reception_errors,
                        positive_receptions=player.positive_receptions,
                        excellent_receptions=player.excellent_receptions
                    )
                    session.add(new_stat)

                # Commit all staged changes specifically for this PDF file
                await session.commit()
                logging.info(f"Successfully ingested match metadata and {len(report.players)} player records from {file_name}.")

            except Exception as e:
                await session.rollback()
                logging.error(f"CRASH OCCURRED while processing {file_name}. Rolling back transaction.", exc_info=True)

    logging.info("Database ingestion pipeline complete.")

if __name__ == "__main__":
    asyncio.run(main())