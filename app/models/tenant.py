from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class Tenant(BaseModel):
    id: UUID
    name: str
    owner_email: EmailStr
    created_at: datetime