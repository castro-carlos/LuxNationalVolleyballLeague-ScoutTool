from pydantic import BaseModel

class PlayerReceptionErrorReport(BaseModel):
    player_name: str
    total_receptions: int
    reception_errors: int
    error_percentage: float

    class Config:
        from_attributes = True


class PlayerAttackVolumeReport(BaseModel):
    player_name: str
    total_attacks: int
    attack_kills: int
    attack_errors: int
    attack_blocked: int
    attack_efficiency: float

    class Config:
        from_attributes = True

class PlayerServiceVolumeReport(BaseModel):
    player_name: str
    total_serves: int
    aces: int
    error_serves: int
    service_efficiency: float
    service_error_rate: float

    class Config:
        from_attributes = True