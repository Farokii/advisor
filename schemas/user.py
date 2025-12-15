from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date
import re


def to_camel(string: str) -> str:
    """将 snake_case 转换为 camelCase（首字母小写）"""
    return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), string)


class UserBase(BaseModel):
    """基础用户信息（不含密码、ID、时间戳）"""
    phone_number: str = Field(...,min_length=6,max_length=20
        #pattern=r"^1[3-9]\d{9}$",
        #description="中国大陆11位手机号",
        #examples=["13812345678"]
    )
    name: str = Field(default="", max_length=50)
    birth: Optional[date] = None
    gender: Optional[str] = Field(default=None, pattern=r"^(male|female|other)$")
    bio: str = Field(default="", max_length=200)
    about: str = Field(default="", max_length=500)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,   # 允许用 snake_case 或 camelCase 赋值
        extra="forbid"           # 禁止传入未定义字段
    )


class UserCreate(UserBase):
    """用户注册：包含密码"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="密码至少8位",
        examples=["MySecurePass123"]
    )


class UserUpdate(BaseModel):
    """用户信息更新：不包含 phone、password、coin（由系统管理）"""
    name: str = Field(default="", max_length=50)
    birth: Optional[date] = None
    gender: Optional[str] = Field(default=None, pattern=r"^(male|female|other)$")
    bio: str = Field(default="", max_length=200)
    about: str = Field(default="", max_length=500)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid"
    )


class UserInDB(UserBase):
    """返回给前端的用户信息（含系统字段）"""
    id: int
    coin: float = Field(ge=0.0, description="用户金币余额")
    created_at: date
    updated_at: date

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True  # 替代 v1 的 orm_mode=True，支持从 ORM 对象构建
    )