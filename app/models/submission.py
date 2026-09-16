from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Submission(BaseModel):
    id: UUID
    widget_id: UUID
    tenant_id: UUID

    name: str | None = None
    email: EmailStr | None = None
    message: str | None = None

    ip_address: str | None = None
    user_agent: str | None = None

    country: str | None = None
    region: str | None = None
    city: str | None = None

    spam: bool = False
    created_at: datetime