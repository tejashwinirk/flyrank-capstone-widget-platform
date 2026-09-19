from uuid import UUID

from app.db.database import get_connection


def create_widget(
    tenant_id: UUID,
    widget_type: str,
    title: str,
    description: str | None,
):
    query = """
        INSERT INTO widgets (
            tenant_id,
            type,
            title,
            description
        )
        VALUES (%s, %s, %s, %s)
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
                (tenant_id, widget_type, title, description),
            )
            row = cursor.fetchone()

        connection.commit()

    return row

def get_tenant_by_email(email: str):
    query = """
        SELECT id, name, owner_email, password_hash, created_at
        FROM tenants
        WHERE owner_email = %s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (email,))
            return cursor.fetchone()