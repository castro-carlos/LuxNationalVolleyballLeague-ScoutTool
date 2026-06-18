from pydantic import BaseModel

class PlayerReceptionErrorReport(BaseModel):
    player_name: str
    total_receptions: int
    reception_errors: int
    error_percentage: float

    class Config:
        from_attributes = True