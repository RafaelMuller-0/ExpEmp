from psycopg.types import none
from pydantic import BaseModel

class CaregiverProfileCreate(BaseModel):
    bio : str | None = None
    experience_years : int | None = None

class CaregiverProfileResponse(BaseModel):
    id : int
    user_id : int
    bio : str
    experience_years : int | None
    approval_status : str
    model_config = {"from_attributes": True}

class CaregiverProfileUpdate(BaseModel):
    bio : str | None = None
    experience_years : int | None = None