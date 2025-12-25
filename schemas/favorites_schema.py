from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime,date
from utils import to_camel

class SaveAdvisorResponse(BaseModel):
    advisor_id: int
    advisor_name: str = Field(..., max_length=20)
    bio : str = Field(..., max_length=50)
    saved_at: datetime
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)