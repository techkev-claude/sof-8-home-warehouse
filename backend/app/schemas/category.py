from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None


class CategoryRead(BaseModel):
    id: int
    name: str
    icon: Optional[str]
    color: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
