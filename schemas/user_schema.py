from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime,date
from utils import to_camel
from models.order_model import OrderType, OrderStatus

class UserBase(BaseModel):
    """基础用户信息（不含密码、ID、时间戳）"""
    phone_number: str = Field(...,min_length=6,max_length=20
        #pattern=r"^1[3-9]\d{9}$",
        #description="中国大陆11位手机号",
        #examples=["13812345678"]
    )
    name: str = Field(default="Anonymous", max_length=50)
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
        max_length=20,
        description="密码至少8位",
        examples=["MySecurePass123"]
    )

class UserLogin(BaseModel):
    phone_number: str = Field(...,min_length=6,max_length=20)
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="密码至少8位",
        examples=["MySecurePass123"]
    )
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # 允许用 snake_case 或 camelCase 赋值
        extra="forbid"  # 禁止传入未定义字段
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
    created_at: datetime
    updated_at: Optional[datetime]=None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True  # 替代 v1 的 orm_mode=True，支持从 ORM 对象构建
    )

class ActiveAdvisors(BaseModel):
    id: int
    name: str = Field(..., max_length=50)
    bio: str = Field(default="", max_length=20)
    work_status: str = Field(..., pattern=r"^(available|busy|urgent_only)$")
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")
#用户端-顾问主页
class AdvisorID(BaseModel):
    id: int
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)
class AdvisorProfile(BaseModel):
    id: int
    name: str = Field(default="", max_length=50)
    bio: str = Field(default="", max_length=20)
    accept_text_reading: bool
    price_text_reading: float = Field(..., ge=3.0, le=36.0, description="每单价格，$")

    accept_audio_reading: bool
    price_audio_reading: float = Field(..., ge=3.0, le=36.0, description="每单价格，$")

    accept_video_reading: bool
    price_video_reading: float = Field(..., ge=3.0, le=36.0, description="每单价格，$")

    accept_live_text_chat: bool
    price_live_text_chat: float = Field(..., ge=1.5, le=18.0, description="每分钟价格，$")

    accept_live_audio_chat: bool
    price_live_audio_chat: float = Field(..., ge=1.5, le=18.0, description="每分钟价格，$")
    about: str = Field(default="", max_length=500)
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )

#用户端-创建订单
class CreateOrder(BaseModel):
    advisor_id: int
    order_type: OrderType = Field(...)
    general_situation: str = Field(..., max_length=3000)
    specific_question: str = Field(..., max_length=200)
    is_urgent: bool
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")
class CreateOrderResponse(BaseModel):
    id: int
    user_id: int
    advisor_id: int
    order_type: OrderType = Field(...)
    order_status: OrderStatus = Field(...)
    is_urgent: bool
    created_at: datetime
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

