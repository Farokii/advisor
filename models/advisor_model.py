from sqlalchemy import Column, Integer, String, Text, Date, Enum,DateTime,Float,Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from SQL.database import Base
from enum import Enum as PyEnum
#服务状态，顾问是否还在平台上工作或活动(类比账号是否登录）
class ServiceStatus(PyEnum):
    out_of_service = "out_of_service"
    in_service = "in_service"
#顾问接单状态。类比上线、忙碌等
class WorkStatus(PyEnum):
    available = "available"
    busy = "busy"
    urgent_only = "urgent_only"#仅接受加急单

class Advisor(Base):
    __tablename__ = "advisors"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False,index=True)
    password = Column(String(255),nullable=False)  # 密码字段使用哈希存储

    name = Column(String(50),nullable=False)
    bio = Column(Text,nullable=True)
    work_experience = Column(String(50),nullable=False)#工作年限
    about = Column(Text, nullable=True)

    service_status=Column(Enum(ServiceStatus), default=ServiceStatus.in_service)#工作状态
    work_status=Column(Enum(WorkStatus), default=WorkStatus.available)
    completed_readings = Column(Integer,nullable=False,default=0) # 完成订单数
    readings=Column(Integer, nullable=False,default=0)#总订单数
    ratings = Column(Float, nullable=False,default=0.0)#顾问评分
    review_count=Column(Integer, nullable=False,default=0)#评论数
    coin = Column(Float, nullable=False,default=100.0)

    accept_text_reading=Column(Boolean, nullable=False,default=True)
    price_text_reading=Column(Float, nullable=False,default=3.0)

    accept_audio_reading = Column(Boolean, nullable=False, default=True)
    price_audio_reading = Column(Float, nullable=False, default=3.0)

    accept_video_reading = Column(Boolean, nullable=False, default=True)
    price_video_reading = Column(Float, nullable=False, default=3.0)

    accept_live_text_chat = Column(Boolean, nullable=False, default=True)
    price_live_text_chat = Column(Float, nullable=False, default=1.5)

    accept_live_audio_chat = Column(Boolean, nullable=False, default=True)
    price_live_audio_chat = Column(Float, nullable=False, default=1.5)

    created_at = Column(DateTime,server_default=func.now())
    updated_at = Column(DateTime,onupdate=func.now())

    orders = relationship("Order",back_populates="advisor")
    reviews = relationship("Review",back_populates="advisor")