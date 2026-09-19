from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from app.db.database import get_connection
from app.services.auth_service import decode_access_token
from app.services.public_widget_service import clear_widget_cache
from app.services.widget_service import create_widget


router = APIRouter(prefix="/widgets", tags=["Widgets"])

security = HTTPBearer()


ALLOWED_WIDGET_TYPES = {
    "signup",
    "contact",
    "cta",
    "popover",
}

ALLOWED_STATUSES = {
    "active",
    "inactive",
}


class WidgetCreateRequest(BaseModel):
    type: str
    title: str = Field(min_length=1, max_length=150)
    description: str | None = None


class WidgetUpdateRequest(BaseModel):
    type: str | None = None
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    description: str | None = None
    status: str | None = None


def get_current_tenant(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    try:
        return decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )


def widget_response(row):
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


@router.post("/", status_code=201)
def create_widget_endpoint(
    payload: WidgetCreateRequest,
    tenant_id: UUID = Depends(get_current_tenant),
):
    if payload.type not in ALLOWED_WIDGET_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid widget type",
        )

    row = create_widget(
        tenant_id=tenant_id,
        widget_type=payload.type,
        title=payload.title,
        description=payload.description,
    )

    return widget_response(row)


@router.get("/")
def list_widgets(
    tenant_id: UUID = Depends(get_current_tenant),
):
    query = """
        SELECT
            id,
            tenant_id,
            type,
            title,
            description,
            status,
            version,
            created_at,
            updated_at
        FROM widgets
        WHERE tenant_id = %s
        ORDER BY created_at DESC;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (tenant_id,))
            rows = cursor.fetchall()

    return [widget_response(row) for row in rows]


@router.get("/{widget_id}")
def get_widget(
    widget_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
):
    query = """
        SELECT
            id,
            tenant_id,
            type,
            title,
            description,
            status,
            version,
            created_at,
            updated_at
        FROM widgets
        WHERE id = %s
          AND tenant_id = %s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (widget_id, tenant_id),
            )
            row = cursor.fetchone()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    return widget_response(row)


@router.patch("/{widget_id}")
def update_widget(
    widget_id: UUID,
    payload: WidgetUpdateRequest,
    tenant_id: UUID = Depends(get_current_tenant),
):
    if (
        payload.type is not None
        and payload.type not in ALLOWED_WIDGET_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid widget type",
        )

    if (
        payload.status is not None
        and payload.status not in ALLOWED_STATUSES
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid widget status",
        )

    if (
        payload.type is None
        and payload.title is None
        and payload.description is None
        and payload.status is None
    ):
        raise HTTPException(
            status_code=400,
            detail="At least one field must be provided",
        )

    query = """
        UPDATE widgets
        SET
            type = COALESCE(%s, type),
            title = COALESCE(%s, title),
            description = COALESCE(%s, description),
            status = COALESCE(%s, status),
            version = version + 1,
            updated_at = NOW()
        WHERE id = %s
          AND tenant_id = %s
        RETURNING
            id,
            tenant_id,
            type,
            title,
            description,
            status,
            version,
            created_at,
            updated_at;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    payload.type,
                    payload.title,
                    payload.description,
                    payload.status,
                    widget_id,
                    tenant_id,
                ),
            )
            row = cursor.fetchone()

        connection.commit()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    # The public widget may already be cached.
    # Clear it immediately so the next public request
    # receives the newly updated version.
    clear_widget_cache(widget_id)

    return widget_response(row)


@router.delete("/{widget_id}", status_code=204)
def delete_widget(
    widget_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant),
):
    query = """
        DELETE FROM widgets
        WHERE id = %s
          AND tenant_id = %s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (widget_id, tenant_id),
            )
            deleted = cursor.rowcount

        connection.commit()

    if deleted == 0:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    # Remove any cached public version after deletion.
    clear_widget_cache(widget_id)

    return None