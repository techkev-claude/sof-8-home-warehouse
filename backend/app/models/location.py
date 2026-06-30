from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class Location(SQLModel, table=True):
    """Lagerort. Unterstuetzt beliebig tiefe Hierarchien ueber parent_id
    (z.B. Raum -> Regal -> Kiste -> Fach), die UI kann sowohl eine flache
    Liste als auch eine Drill-Down-Navigation darauf aufbauen."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)           # z.B. "Kiste A", "Regal 2"
    description: Optional[str] = None
    parent_id: Optional[int] = Field(default=None, foreign_key="location.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
