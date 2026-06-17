# schemas.py
from pydantic import BaseModel

class TeamResponse(BaseModel):
    id: int
    team_name: str

    class ConfigDict:
        from_attributes = True