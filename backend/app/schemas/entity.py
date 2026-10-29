"""Entity Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EntityResponse(BaseModel):
    """Entity response representation."""

    id: UUID
    name: str
    type: str
    confidence: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EntityCreate(BaseModel):
    """Schema for creating an entity."""

    name: str
    type: str
    confidence: float = 1.0
