from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Tenant(BaseModel):
    id: UUID
    name: str
    owner_email: EmailStr
    password_hash: str | None = None
    created_at: datetime