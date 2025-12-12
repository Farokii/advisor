from sqlalchemy import Column, Integer, String, Text, Date, Enum, TIMESTAMP, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from enum import Enum as PyEnum

Base = declarative_base()

# 用户性别枚举
class Gender(PyEnum):
    male = "male"
    female = "female"
    other = "other"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True)
    password = Column(String(255))  # 密码字段使用哈希存储
    name = Column(String(50))
    birth = Column(Date)
    gender = Column(Enum(Gender))
    bio = Column(Text)
    about = Column(Text)
    coin = Column(Integer, default=0)
    created_at = Column(TIMESTAMP)

