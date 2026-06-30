from pydantic import BaseModel
from datetime import datetime


class ItemImageRead(BaseModel):
    id: int
    item_id: int
    filename: str
    thumbnail_filename: str
    is_primary: bool
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True
