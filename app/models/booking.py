from datetime import datetime, timezone
from app.models.base import Base

from sqlalchemy import ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.care_recipient import CareRecipient
    from app.models.caregiver_profile import CaregiverProfile
    from app.models.user import User

class Booking(Base):
    __tablename__ = 'booking'
    __table_args__ = (CheckConstraint('end_at > start_at', name='booking_start_end_check'),)
    id : Mapped[int] = mapped_column(primary_key=True)
    requester_user_id : Mapped[int] = mapped_column(ForeignKey('user.id'))
    care_recipient_id : Mapped[int] = mapped_column(ForeignKey('care_recipient.id'))
    caregiver_profile_id : Mapped[int | None] = mapped_column(ForeignKey('caregiver_profile.id'))
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    address: Mapped[str]
    status: Mapped[str] = mapped_column(default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
    caregiver: Mapped["CaregiverProfile | None"] = relationship(back_populates="bookings")
    care_recipient: Mapped["CareRecipient"] = relationship(back_populates="bookings")
    requester : Mapped["User"] = relationship(back_populates="bookings_as_requester")
