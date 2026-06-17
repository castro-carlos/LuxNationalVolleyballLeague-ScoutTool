from pydantic import BaseModel, computed_field

class TeamPlayerErrorRank(BaseModel):
    player_name: str
    total_receptions: int
    reception_errors: int

    @computed_field
    def error_percentage(self) -> float:
        if self.total_receptions == 0:
            return 0.0
        # Calculate percentage and round to 1 decimal place
        return round((self.reception_errors / self.total_receptions) * 100, 2)

    class Config:
        from_attributes = True