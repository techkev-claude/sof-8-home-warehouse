from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.item import ItemStatus
from app.schemas.item_image import ItemImageRead


class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    connector_a: Optional[str] = None
    connector_b: Optional[str] = None
    cable_length_cm: Optional[int] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    location_id: Optional[int] = None

    # Optional von der Android-App nach On-Device-KI-Analyse mitgeliefert,
    # siehe ANDROID_INTEGRATION.md
    ai_analyzed: bool = False
    ai_confidence: Optional[float] = None
    ai_raw_response: Optional[str] = None


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    connector_a: Optional[str] = None
    connector_b: Optional[str] = None
    cable_length_cm: Optional[int] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    location_id: Optional[int] = None
    ai_analyzed: Optional[bool] = None
    ai_confidence: Optional[float] = None
    ai_raw_response: Optional[str] = None


class ItemCheckOut(BaseModel):
    usage_purpose_id: Optional[int] = None
    usage_note: Optional[str] = None


class ItemCheckIn(BaseModel):
    location_id: int


class ItemRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category_id: Optional[int]
    connector_a: Optional[str]
    connector_b: Optional[str]
    cable_length_cm: Optional[int]
    color: Optional[str]
    brand: Optional[str]
    status: ItemStatus
    location_id: Optional[int]
    usage_purpose_id: Optional[int]
    usage_note: Optional[str]
    ai_analyzed: bool
    ai_confidence: Optional[float]
    ai_raw_response: Optional[str]
    created_by_id: Optional[int]
    updated_by_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    stored_at: Optional[datetime]
    checked_out_at: Optional[datetime]
    images: List[ItemImageRead] = []

    class Config:
        from_attributes = True
