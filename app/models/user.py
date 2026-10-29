from datetime import datetime, timezone

from app.models.base import Base

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base):
    __tablename__ = 'user'
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str]
    email : Mapped[str] = mapped_column(nullable=False, unique=True)
    password_hash : Mapped[str] = mapped_column(String, nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda:datetime.now(timezone.utc))
    caregiver_profile: Mapped["CaregiverProfile | None"] = relationship(back_populates="user")