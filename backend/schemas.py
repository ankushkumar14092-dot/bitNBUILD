from datetime import date
from pydantic import BaseModel, Field

class ScenarioInput(BaseModel):
    scenario_id: str
    commodity: str
    cargo_volume_tonnes:float = Field(gt=0)
    origin:str
    destination_port:str
    laycan_start:date
    laycan_end:date
    target_arrival:date
    inventory_tonnes:float = Field(ge=0)
    daily_consumption_tonnes:float = Field(gt=0)
    safety_buffer_days:float = Field(ge=0)
    currency:str = Field(min_length=3, max_length=3)
    freight_rate_per_tonne:float = Field(ge=0)
    cargo_value: float = Field(ge=0)
    insurance_rate: float = Field(ge=0)
    port_charge: float = Field(ge=0)
    expected_delay_days : float = Field(ge=0)
    demurrage_rate_per_day : float = Field(ge=0)
    demurrage_free_days: float = Field(default=0, ge=0)
