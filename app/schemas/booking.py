from datetime import datetime
from pydantic import BaseModel


class BookingCreate(BaseModel):
    care_recipient_id: int
    caregiver_profile_id: int
    start_at: datetime
    end_at: datetime
    address: str


class BookingResponse(BaseModel):
    id: int
    requester_user_id: int
    care_recipient_id: int
    caregiver_profile_id: int | None
    start_at: datetime
    end_at: datetime
    address: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}

class BookingStatusUpdate(BaseModel):
    status: str