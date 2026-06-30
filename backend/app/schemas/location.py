from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LocationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None


class LocationRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    parent_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class LocationTreeNode(LocationRead):
    """Rekursiver Baum fuer die Drill-Down-Navigation in der UI."""

    children: List["LocationTreeNode"] = []


LocationTreeNode.model_rebuild()
