from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from app.db.database import get_connection
from app.services.background_jobs import (
    queue_submission_notification,
)
from app.services.geo_service import get_geo_data
from app.services.rate_limit import limiter


router = APIRouter(
    prefix="/public",
    tags=["Public Submissions"],
)


class SubmissionRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    email: EmailStr
    message: str | None = Field(
        default=None,
        max_length=5000,
    )
    website: str | None = Field(
        default=None,
        max_length=500,
    )


@router.post(
    "/widgets/{widget_id}/submissions",
    status_code=201,
)
@limiter.limit("5/minute")
def create_submission(
    widget_id: UUID,
    payload: SubmissionRequest,
    request: Request,
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
        max_length=255,
    ),
):
    widget_query = """
        SELECT id, tenant_id, status
        FROM widgets
        WHERE id = %s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                widget_query,
                (widget_id,),
            )
            widget = cursor.fetchone()

    if not widget:
        raise HTTPException(
            status_code=404,
            detail="Widget not found",
        )

    if widget[2] != "active":
        raise HTTPException(
            status_code=404,
            detail="Widget is inactive",
        )

    # Honeypot protection.
    if payload.website:
        return {
            "status": "accepted",
            "message": "Submission received",
        }

    # Return the original submission when the same
    # idempotency key is reused for this widget.
    if idempotency_key:
        existing_query = """
            SELECT id, created_at
            FROM submissions
            WHERE widget_id = %s
              AND idempotency_key = %s;
        """

        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    existing_query,
                    (widget_id, idempotency_key),
                )
                existing = cursor.fetchone()

        if existing:
            return {
                "id": str(existing[0]),
                "status": "received",
                "created_at": existing[1],
                "idempotent": True,
            }

    tenant_id = widget[1]

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    geo = get_geo_data(client_ip)

    insert_query = """
        INSERT INTO submissions (
            widget_id,
            tenant_id,
            name,
            email,
            message,
            ip_address,
            user_agent,
            country,
            region,
            city,
            spam,
            idempotency_key
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            FALSE,
            %s
        )
        RETURNING id, created_at;
    """

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    insert_query,
                    (
                        widget_id,
                        tenant_id,
                        payload.name,
                        str(payload.email),
                        payload.message,
                        client_ip,
                        user_agent,
                        geo["country"],
                        geo["region"],
                        geo["city"],
                        idempotency_key,
                    ),
                )

                row = cursor.fetchone()

            connection.commit()

    except Exception:
        # A concurrent request may have inserted the same
        # idempotency key between our lookup and INSERT.
        if idempotency_key:
            existing_query = """
                SELECT id, created_at
                FROM submissions
                WHERE widget_id = %s
                  AND idempotency_key = %s;
            """

            with get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        existing_query,
                        (widget_id, idempotency_key),
                    )
                    existing = cursor.fetchone()

            if existing:
                return {
                    "id": str(existing[0]),
                    "status": "received",
                    "created_at": existing[1],
                    "idempotent": True,
                }

        raise HTTPException(
            status_code=500,
            detail="Unable to store submission",
        )

    submission_id = str(row[0])

    queue_submission_notification(
        submission_id=submission_id,
        widget_id=str(widget_id),
        email=str(payload.email),
    )

    return {
        "id": submission_id,
        "status": "received",
        "created_at": row[1],
        "idempotent": False,
    }