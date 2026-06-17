# api/teams.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List

# Clean downstream imports—no looking back at main!
from db.models import Team
from db.database import get_db
from schemas.teams import TeamResponse

router = APIRouter(
    prefix="/teams",
    tags=["Teams Management"]
)

@router.get("", response_model=List[TeamResponse])
def get_all_teams(db: Session = Depends(get_db)):
    try:
        stmt = select(Team).order_by(Team.team_name)
        return db.scalars(stmt).all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))