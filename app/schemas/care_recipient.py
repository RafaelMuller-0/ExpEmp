from datetime import datetime
from pydantic import BaseModel


class CareRecipientCreate(BaseModel):
    name: str
    care_notes: str | None = None


class CareRecipientResponse(BaseModel):
    id: int
    created_by_user_id: int
    name: str
    care_notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

class CareRecipientUpdate(BaseModel):
    name: str | None = None
    care_notes: str | None = None