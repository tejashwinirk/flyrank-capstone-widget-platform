from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Widget(BaseModel):
    id: UUID
    tenant_id: UUID
    type: str
    title: str
    description: str | None = None
    status: str = Field(default="active")
    version: int = Field(default=1, ge=1)
    created_at: datetime
    updated_at: datetime