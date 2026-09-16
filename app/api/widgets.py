from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.widget_service import create_widget


router = APIRouter(prefix="/widgets", tags=["Widgets"])


class WidgetCreateRequest(BaseModel):
    tenant_id: UUID
    type: str
    title: str = Field(min_length=1, max_length=150)
    description: str | None = None


@router.post("/", status_code=201)
def create_widget_endpoint(payload: WidgetCreateRequest):
    allowed_types = {"signup", "contact", "cta", "popover"}

    if payload.type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid widget type",
        )

    row = create_widget(
        tenant_id=payload.tenant_id,
        widget_type=payload.type,
        title=payload.title,
        description=payload.description,
    )

    return {
        "id": str(row[0]),
        "tenant_id": str(row[1]),
        "type": row[2],
        "title": row[3],
        "description": row[4],
        "status": row[5],
        "version": row[6],
        "created_at": row[7],
        "updated_at": row[8],
    }