from sqlalchemy import Column, Integer, String, Text, Date, Enum,DateTime,Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from SQL.database import Base
from enum import Enum as PyEnum

# 用户性别枚举
class Gender(PyEnum):
    male = "male"
    female = "female"
    other = "other"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False,index=True)
    password = Column(String(255),nullable=False)  # 密码字段使用哈希存储
    name = Column(String(50),default="Drifter")
    birth = Column(Date,nullable=True)
    gender = Column(Enum(Gender),default=Gender.other)
    bio = Column(Text,nullable=True)
    about = Column(Text, nullable=True)
    coin = Column(Float, default=100.0)
    created_at = Column(DateTime,server_default=func.now())
    updated_at = Column(DateTime,onupdate=func.now())

    orders = relationship("Order",back_populates="user")