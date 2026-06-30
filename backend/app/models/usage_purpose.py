from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class UsagePurpose(SQLModel, table=True):
    __tablename__ = "usage_purpose"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)          # z.B. "Gaming-PC", "Heimkino"
    description: Optional[str] = None
    # Wenn True, muss beim Checkout mit diesem Zweck zwingend ein Freitext
    # (usage_note) angegeben werden ("Zusatzinformation erfassen").
    requires_note: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
