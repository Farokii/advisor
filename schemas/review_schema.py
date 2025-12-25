from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime,date
from utils import to_camel
from models.order_model import OrderStatus, OrderType
from datetime import datetime

class ReviewInfo(BaseModel):
    rating: float = Field(..., ge=1.0, le=5.0, description="Review rating")
    review_text: Optional[str] = Field(None, max_length=300, description="Review text")
    tip: Optional[float] = Field(None, ge=0.0, le=5.0, description="tip")
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")

class AdvisorReviewResponse(BaseModel):

    order_id: int
    user_id: int
    advisor_id: int
    user_name: str = Field(..., max_length=50)
    order_type: OrderType
    rating: float = Field(..., ge=1.0, le=5.0, description="Review rating")
    review_text: Optional[str] = Field(None, max_length=300, description="Review text")
    created_at: Optional[datetime] = None
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

class UserReviewResponse(AdvisorReviewResponse):
    id: Optional[int] = None
    tip: Optional[float] = Field(None, ge=0.0, le=5.0, description="tip")

