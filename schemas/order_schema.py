from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime,date
from utils import to_camel
from models.order_model import OrderStatus, OrderType
from models.user_model import Gender
#订单列表
class OrderListResponse(BaseModel):
    order_id: int
    related_id: int
    name: str # 关联者名字
    order_type: OrderType = Field(...)
    order_status: OrderStatus = Field(...)
    is_urgent: bool
    specific_question: str = Field(..., max_length=200)
    created_at: datetime
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class OrderDetailsResponse(BaseModel):
    order_id: int
    user_id: int
    user_name: str
    birth: date
    gender: Gender
    advisor_id: int
    advisor_name: str
    order_status: OrderStatus
    order_type: OrderType
    is_urgent: bool
    general_situation: str = Field(..., max_length=5000)
    specific_question: str = Field(..., max_length=200)
    reply: Optional[str] = Field(None, max_length=5000)
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class CoinTransResponse(BaseModel):
    type: str = Field(...)
    credit: str = Field(...)
    time: str = Field(...)
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)