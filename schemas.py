from pydantic import BaseModel

class TeamResponse(BaseModel):
    id: int
    team_name: str

    class Config:
        from_attributes = True

class TeamCreateInput(BaseModel):
    team_name: str