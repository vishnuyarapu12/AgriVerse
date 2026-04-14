"""
Pydantic models for farmer utility APIs (weather, one-tap solutions, reminders).
"""
from pydantic import BaseModel, Field, field_validator


class FarmerWeatherResponse(BaseModel):
    """Open-Meteo based spray advice with smart window recommendations — GET /weather"""

    temperature: float = Field(..., description="Air temperature (°C)")
    wind_speed: float = Field(..., description="Wind at 10m (km/h, Open-Meteo default)")
    advice: str = Field(..., description="Farmer spray recommendation")
    spray_window: dict = Field(..., description="Ideal spraying window analysis from 24h forecast")


class SolutionCard(BaseModel):
    """Structured one-tap solution for GET /solution/{disease}"""

    disease: str
    medicine: str
    dosage: str
    time: str
    note: str


class SetReminderRequest(BaseModel):
    """Body for POST /set-reminder"""

    message: str = Field(..., min_length=1, max_length=500)
    delay_seconds: int = Field(..., ge=1, le=604800, description="Delay before reminder (max 7 days)")

    @field_validator("message")
    @classmethod
    def strip_message(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("message cannot be empty")
        return s


class SetReminderResponse(BaseModel):
    """Acknowledgement after scheduling a reminder"""

    status: str
    job_id: str
    fires_at_utc: str
    message: str
