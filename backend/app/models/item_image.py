from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class ItemImage(SQLModel, table=True):
    """Ein Item kann mehrere Bilder haben (z.B. verschiedene Winkel,
    Stecker-Nahaufnahmen). is_primary markiert das Titelbild, das in
    Listen/Thumbnails verwendet wird."""

    __tablename__ = "item_image"

    id: Optional[int] = Field(default=None, primary_key=True)
    item_id: int = Field(foreign_key="item.id", index=True)
    filename: str
    thumbnail_filename: str
    is_primary: bool = Field(default=False)
    sort_order: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
