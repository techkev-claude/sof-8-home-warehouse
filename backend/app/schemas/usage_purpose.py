from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UsagePurposeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    requires_note: bool = False


class UsagePurposeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    requires_note: Optional[bool] = None


class UsagePurposeRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    requires_note: bool
    created_at: datetime

    class Config:
        from_attributes = True
