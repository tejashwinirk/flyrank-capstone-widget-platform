from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.database import get_connection
from app.services.auth_service import decode_access_token


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

security = HTTPBearer()


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


@router.get("/submissions")
def list_submissions(
    widget_id: UUID | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    tenant_id: UUID = Depends(get_current_tenant),
):
    query = """
        SELECT
            id,
            widget_id,
            name,
            email,
            message,
            country,
            region,
            city,
            spam,
            created_at
        FROM submissions
        WHERE tenant_id = %s
    """

    params: list = [tenant_id]

    if widget_id is not None:
        query += " AND widget_id = %s"
        params.append(widget_id)

    query += """
        ORDER BY created_at DESC
        LIMIT %s
        OFFSET %s;
    """

    params.extend([limit, offset])

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

    return {
        "items": [
            {
                "id": str(row[0]),
                "widget_id": str(row[1]),
                "name": row[2],
                "email": row[3],
                "message": row[4],
                "country": row[5],
                "region": row[6],
                "city": row[7],
                "spam": row[8],
                "created_at": row[9],
            }
            for row in rows
        ],
        "limit": limit,
        "offset": offset,
    }


@router.get("/analytics")
def get_analytics(
    widget_id: UUID | None = Query(default=None),
    tenant_id: UUID = Depends(get_current_tenant),
):
    base_filter = "tenant_id = %s"
    params: list = [tenant_id]

    if widget_id is not None:
        base_filter += " AND widget_id = %s"
        params.append(widget_id)

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM submissions
                WHERE {base_filter};
                """,
                params,
            )
            total_submissions = cursor.fetchone()[0]

            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM submissions
                WHERE {base_filter}
                  AND spam = TRUE;
                """,
                params,
            )
            spam_submissions = cursor.fetchone()[0]

            cursor.execute(
                f"""
                SELECT
                    country,
                    COUNT(*) AS submission_count
                FROM submissions
                WHERE {base_filter}
                GROUP BY country
                ORDER BY submission_count DESC;
                """,
                params,
            )
            countries = cursor.fetchall()

            cursor.execute(
                f"""
                SELECT
                    DATE(created_at) AS submission_date,
                    COUNT(*) AS submission_count
                FROM submissions
                WHERE {base_filter}
                GROUP BY DATE(created_at)
                ORDER BY submission_date;
                """,
                params,
            )
            daily = cursor.fetchall()

    return {
        "total_submissions": total_submissions,
        "spam_submissions": spam_submissions,
        "countries": [
            {
                "country": row[0] or "Unknown",
                "count": row[1],
            }
            for row in countries
        ],
        "daily_submissions": [
            {
                "date": row[0].isoformat(),
                "count": row[1],
            }
            for row in daily
        ],
    }