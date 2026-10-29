from app.models.base import Base

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class CaregiverProfile(Base):
    __tablename__ = 'caregiver_profile'
    id : Mapped[int] = mapped_column(primary_key=True)
    user_id : Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, unique=True)
    bio : Mapped[str | None]
    experience_years : Mapped[int | None]
    approval_status : Mapped[str] = mapped_column(default="pending")
    user : Mapped["User"] = relationship(back_populates="caregiver_profile")