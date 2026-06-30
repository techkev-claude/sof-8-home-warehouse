from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    icon: Optional[str] = None        # emoji oder icon-name
    color: Optional[str] = None       # hex-farbe fuer UI
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
