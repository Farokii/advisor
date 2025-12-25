from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, Float, func
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from SQL.database import Base
from models.order_model import OrderType

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    advisor_id = Column(Integer, ForeignKey('advisors.id'), nullable=False, index=True)

    user_name = Column(String(50), nullable=False)
    order_type = Column(Enum(OrderType), nullable=False, index=True)
    rating = Column(Float, nullable=False) # 订单评分
    review_text = Column(String(300), nullable=True, default="")
    tip = Column(Float, nullable=True, default=0.0) # 打赏

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    order = relationship("Order", back_populates="review")
    user = relationship("User", back_populates="reviews")
    advisor = relationship("Advisor", back_populates="reviews")

