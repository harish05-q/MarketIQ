"""Briefing Pydantic schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BriefingSection(BaseModel):
    """A section within a briefing."""

    title: str
    content: str
    key_points: list[str] = Field(default_factory=list)


class BriefingResponse(BaseModel):
    """Briefing response representation."""

    id: UUID
    briefing_type: str
    content: str
    sections: list[BriefingSection] = Field(default_factory=list)
    briefing_date: date
    generated_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BriefingDetailResponse(BaseModel):
    """Standard single-briefing API response."""

    success: bool = True
    data: BriefingResponse | None = None
