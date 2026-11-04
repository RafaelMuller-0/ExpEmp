from datetime import datetime
from pydantic import BaseModel


class AvailabilityCreate(BaseModel):
    start_at: datetime
    end_at: datetime

class AvailabilityResponse(BaseModel):
    id: int
    caregiver_profile_id: int
    start_at: datetime
    end_at: datetime
    model_config = {"from_attributes": True}

class AvailabilityUpdate(BaseModel):
    start_at: datetime | None = None
    end_at: datetime | None = None

class FreeIntervalResponse(BaseModel):
    start_at: datetime
    end_at: datetime