from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, Float, func
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from SQL.database import Base
from models import user_model,advisor_model

# 定义订单状态
class OrderStatus(PyEnum):
    pending = "pending"
    completed = "completed"
    expired = "expired"


# 定义订单类型（对应你的五种服务）
class OrderType(PyEnum):
    text_reading_24h = "text_reading_24h"
    audio_reading_24h = "audio_reading_24h"
    video_reading_24h = "video_reading_24h"
    live_text_chat = "live_text_chat"
    live_audio_chat = "live_audio_chat"


class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)  # 关联用户
    advisor_id = Column(Integer, ForeignKey('advisors.id'), nullable=False, index=True)  # 关联顾问

    order_type = Column(Enum(OrderType), nullable=False, index=True)  # 订单类型

    general_situation = Column(String(3000), nullable=False)  # 一般个人情况
    specific_question = Column(String(200), nullable=False)  # 具体问题
    reply = Column(String(1000), nullable=True) # 顾问回复（暂时只能回复reading订单）

    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False, index=True)  # 状态
    completed_at = Column(DateTime, nullable=True)  # 完成时间

    is_urgent = Column(Boolean, default=False, nullable=False, index=True)  # 是否加急

    # 价格相关
    base_price = Column(Float, nullable=False)  # 基础价格（下单时顾问设定）
    final_amount = Column(Float, nullable=True)  # 最终支付金额

    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)  # 创建时间
    updated_at = Column(DateTime, onupdate=func.now())  # 更新时间

    #关联定义
    # user = relationship("User", back_populates="orders")
    # advisor = relationship("Advisor", back_populates="orders")
