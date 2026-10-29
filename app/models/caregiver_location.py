from datetime import datetime, timezone
from app.models.base import Base

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

class CaregiverLocation(Base):
    __tablename__ = 'caregiver_location'
    id : Mapped[int] = mapped_column(primary_key=True)
    caregiver_profile_id : Mapped[int] = mapped_column(ForeignKey('caregiver_profile.id'), unique=True, nullable=False)
    latitude : Mapped[float]
    longitude : Mapped[float]
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc), onupdate=lambda:datetime.now(timezone.utc))
