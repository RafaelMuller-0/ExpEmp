from datetime import datetime, timezone

from app.models.base import Base

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.booking import Booking

class CareRecipient(Base):
    __tablename__ = 'care_recipient'
    id : Mapped[int] = mapped_column(primary_key=True)
    created_by_user_id : Mapped[int] = mapped_column(ForeignKey('user.id'))
    name : Mapped[str] = mapped_column(nullable=False)
    care_notes : Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    user : Mapped["User"] = relationship(back_populates="care_recipients")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="care_recipient")