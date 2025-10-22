from datetime import date
from pydantic import BaseModel, ConfigDict


class LineBotUsageBase(BaseModel):
    push_count: int = 0


class LineBotUsageCreate(LineBotUsageBase):
    date: date


class LineBotUsageUpdate(BaseModel):
    push_count: int


class LineBotUsage(LineBotUsageBase):
    date: date

    model_config = ConfigDict(from_attributes=True)
