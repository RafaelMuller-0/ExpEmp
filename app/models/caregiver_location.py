from datetime import datetime, timezone
from app.models.base import Base

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.caregiver_profile import CaregiverProfile

class CaregiverLocation(Base):
    __tablename__ = 'caregiver_location'
    id : Mapped[int] = mapped_column(primary_key=True)
    caregiver_profile_id : Mapped[int] = mapped_column(ForeignKey('caregiver_profile.id'), unique=True, nullable=False)
    latitude : Mapped[float]
    longitude : Mapped[float]
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc), onupdate=lambda:datetime.now(timezone.utc))
    caregiver_profile: Mapped["CaregiverProfile"] = relationship(back_populates="location")