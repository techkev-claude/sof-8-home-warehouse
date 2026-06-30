from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"      # volle Rechte inkl. Benutzerverwaltung
    MEMBER = "member"    # darf Items/Orte/Kategorien/Zwecke verwalten
    VIEWER = "viewer"    # nur Lesezugriff


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    role: UserRole = Field(default=UserRole.MEMBER)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
