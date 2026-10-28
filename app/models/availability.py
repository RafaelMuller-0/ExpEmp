from datetime import datetime
from app.models.base import Base

from sqlalchemy import ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

class Availability(Base):
    __tablename__ = 'availability'
    __table_args__ = (CheckConstraint('end_at > start_at',name='availability_start_end_check'),)
    id : Mapped[int] = mapped_column(primary_key=True)
    caregiver_profile_id : Mapped[int] = mapped_column(ForeignKey('caregiver_profile.id'))
    start_at : Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at : Mapped[datetime] = mapped_column(DateTime(timezone=True))