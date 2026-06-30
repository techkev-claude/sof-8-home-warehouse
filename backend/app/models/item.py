from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ItemStatus(str, Enum):
    STORED = "stored"           # eingelagert
    IN_USE = "in_use"           # ausgelagert/in Verwendung
    LOST = "lost"                # vermisst
    DEFECT = "defect"           # defekt


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None

    # Klassifizierung
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    # Kabelspezifische Felder (erweiterbar per Migration)
    connector_a: Optional[str] = None       # z.B. "USB-A", "USB-C"
    connector_b: Optional[str] = None       # z.B. "USB-C", "HDMI"
    cable_length_cm: Optional[int] = None
    color: Optional[str] = None
    brand: Optional[str] = None

    # Lager & Status
    status: ItemStatus = Field(default=ItemStatus.STORED)
    location_id: Optional[int] = Field(default=None, foreign_key="location.id")
    usage_purpose_id: Optional[int] = Field(
        default=None, foreign_key="usage_purpose.id"
    )
    usage_note: Optional[str] = None        # Freitext bei Auslagerung

    # KI-Metadaten (befuellt von der Android-App nach On-Device-Analyse,
    # siehe ANDROID_INTEGRATION.md)
    ai_analyzed: bool = Field(default=False)
    ai_confidence: Optional[float] = None
    ai_raw_response: Optional[str] = None

    # Nachvollziehbarkeit (Multi-User)
    created_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    updated_by_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    stored_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
