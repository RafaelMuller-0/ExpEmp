from datetime import datetime, timezone

from app.models.base import Base

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.care_recipient import CareRecipient
    from app.models.caregiver_profile import CaregiverProfile
    from app.models.booking import Booking


class User(Base):
    __tablename__ = 'user'
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str]
    email : Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash : Mapped[str] = mapped_column(String, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
    caregiver_profile: Mapped["CaregiverProfile | None"] = relationship(back_populates="user")
    care_recipients: Mapped[list["CareRecipient"]] = relationship(back_populates="user")
    bookings_as_requester: Mapped[list["Booking"]] = relationship(back_populates="requester")