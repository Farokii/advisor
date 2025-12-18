from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime,date
from utils import to_camel

class AdvisorBase(BaseModel):
    """基础顾问信息（不含密码、ID、时间戳）"""
    phone_number: str = Field(...,min_length=6,max_length=20
        #pattern=r"^1[3-9]\d{9}$",
        #description="中国大陆11位手机号",
        #examples=["13812345678"]
    )
    name: str = Field(..., max_length=50)
    bio: str = Field(default="", max_length=20)
    about: str = Field(default="", max_length=500)
    work_experience: str = Field(..., max_length=50)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,   # 允许用 snake_case 或 camelCase 赋值
        extra="forbid"           # 禁止传入未定义字段
    )
#注册
class AdvisorCreate(AdvisorBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="密码至少8位",
        examples=["MySecurePass123"]
    )
class AdvisorCreateResponse(AdvisorBase):
    """顾问注册返回信息"""
    id: int
    coin: float = Field(ge=0.0, description="用户金币余额")
    service_status: str = Field(...,pattern=r"^(out_of_service|in_service|)$")
    work_status: str = Field(...,pattern=r"^(available|busy|urgent_only)$")
    readings: int = Field(...,ge=0)#总订单数
    ratings : float = Field(...,ge=0.0,le=5.0)#顾问评分
    review_count : int = Field(...,ge=0)#评论数

    accept_text_reading : bool
    price_text_reading : float = Field(...,ge=3.0,le=36.0,description="每单价格，$")

    accept_audio_reading : bool
    price_audio_reading : float = Field(...,ge=3.0,le=36.0,description="每单价格，$")

    accept_video_reading : bool
    price_video_reading : float = Field(...,ge=3.0,le=36.0,description="每单价格，$")

    accept_live_text_chat :bool
    price_live_text_chat : float = Field(...,ge=1.5,le=18.0,description="每分钟价格，$")

    accept_live_audio_chat : bool
    price_live_audio_chat : float = Field(...,ge=1.5,le=18.0,description="每分钟价格，$")

    created_at: datetime
    updated_at: Optional[datetime]=None

    model_config = ConfigDict(
        from_attributes=True
    )
#登录
class AdvisorLogin(BaseModel):
    phone_number: str = Field(..., min_length=6, max_length=20)
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
#信息修改
class AdvisorUpdateProfile(BaseModel):
    name : str = Field(...,max_length=50)
    bio: str = Field(default="", max_length=20)
    work_experience: str = Field(default="", max_length=50)
    about: str = Field(default="", max_length=500)
    model_config = ConfigDict(alias_generator=to_camel,populate_by_name=True, extra="forbid" )
class AdvisorUpdateProfileResponse(AdvisorBase):
    id: int
    updated_at: datetime
    model_config = ConfigDict(
        from_attributes=True
    )
#主页
class ProfileResponse(BaseModel):
    id: int
    name: str = Field(..., max_length=50)
    coin: float = Field(ge=0.0, description="用户金币余额")
    service_status: str = Field(..., pattern=r"^(out_of_service|in_service|)$")
    readings: int = Field(..., ge=0)  # 总订单数
    ratings: float = Field(..., ge=0.0,le=5.0)  # 顾问评分
    review_count: int = Field(..., ge=0)  # 评论数
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid",from_attributes=True)
#接单状态修改
class UpdateWorkStatus(BaseModel):
    work_status: str = Field(...,pattern=r"^(available|busy|urgent_only)$")
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")
class UpdateWorkStatusResponse(BaseModel):
    id: int
    name: str = Field(..., max_length=50)
    work_status: str = Field(..., pattern=r"^(available|busy|urgent_only)$")
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True,from_attributes=True)

#服务状态修改
class UpdateServiceStatus(BaseModel):
    service_status: str = Field(...,pattern=r"^(out_of_service|in_service)$")
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")
class UpdateServiceStatusResponse(BaseModel):
    id: int
    name: str = Field(..., max_length=50)
    service_status: str = Field(..., pattern=r"^(out_of_service|in_service)$")
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True,from_attributes=True)

#价格修改
class UpdatePrice(BaseModel):
    accept_text_reading: Optional[bool] = None
    price_text_reading: Optional[float] = Field(None, ge=3.0, le=36.0, description="每单价格，$")

    accept_audio_reading: Optional[bool] = None
    price_audio_reading: Optional[float] = Field(None, ge=3.0, le=36.0, description="每单价格，$")

    accept_video_reading: Optional[bool] = None
    price_video_reading: Optional[float] = Field(None, ge=3.0, le=36.0, description="每单价格，$")

    accept_live_text_chat: Optional[bool] = None
    price_live_text_chat: Optional[float] = Field(None, ge=1.5, le=18.0, description="每分钟价格，$")

    accept_live_audio_chat: Optional[bool] = None
    price_live_audio_chat: Optional[float] = Field(None, ge=1.5, le=18.0, description="每分钟价格，$")
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")
class UpdatePriceResponse(BaseModel):
    id: int
    name: str = Field(..., max_length=50)
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

    updated_at: Optional[datetime] = None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True,from_attributes=True)