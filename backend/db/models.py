from datetime import date
from typing import Optional
from sqlalchemy import String, Integer, Date, Boolean, ForeignKey, Identity
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """Abstract base class that maintains a catalog of tables and classes."""
    pass

class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    team_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

class Match(Base):
    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    file_origin: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    match_date: Mapped[Optional[date]] = mapped_column(Date)
    season: Mapped[Optional[str]] = mapped_column(String)
    home_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"))
    away_team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"))

class PlayerMatchStat(Base):
    __tablename__ = "player_match_stats"
    id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"))

    jersey: Mapped[Optional[int]] = mapped_column(Integer)
    player_name: Mapped[Optional[str]] = mapped_column(String)
    team_played_for_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"))
    is_libero: Mapped[Optional[bool]] = mapped_column(Boolean)

    points_total: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    points_break: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    plus_minus: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    service_total: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    service_errors: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    service_aces: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    total_receptions: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    reception_errors: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    positive_receptions: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    excellent_receptions: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    attack_total: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    attack_errors: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    attack_blocked: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    attack_kills: Mapped[Optional[int]] = mapped_column(Integer, default=0)

    block_points: Mapped[Optional[int]] = mapped_column(Integer, default=0)