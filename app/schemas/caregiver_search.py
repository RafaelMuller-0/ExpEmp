from pydantic import BaseModel


class CaregiverSearchResponse(BaseModel):
    caregiver_profile_id: int
    user_id: int
    name: str
    bio: str | None
    experience_years: int | None

    model_config = {"from_attributes": True}