from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, Float, func
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from SQL.database import Base

class Favorites(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    advisor_id = Column(Integer, ForeignKey('advisors.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="favorites")
    advisor = relationship("Advisor", back_populates="favorites")
