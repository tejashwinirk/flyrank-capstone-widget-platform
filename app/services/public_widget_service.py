import time
from uuid import UUID

from app.db.database import get_connection


CACHE_TTL_SECONDS = 60

_widget_cache: dict[str, tuple[float, dict]] = {}


def get_public_widget(widget_id: UUID):
    cache_key = str(widget_id)
    now = time.time()

    cached = _widget_cache.get(cache_key)

    if cached:
        cached_at, data = cached

        if now - cached_at < CACHE_TTL_SECONDS:
            return data

        del _widget_cache[cache_key]

    query = """
        SELECT
            id,
            type,
            title,
            description,
            status,
            version,
            updated_at
        FROM widgets
        WHERE id = %s;
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (widget_id,))
            row = cursor.fetchone()

    if not row:
        return None

    if row[4] != "active":
        return None

    data = {
        "id": str(row[0]),
        "type": row[1],
        "title": row[2],
        "description": row[3],
        "status": row[4],
        "version": row[5],
        "updated_at": row[6],
    }

    _widget_cache[cache_key] = (now, data)

    return data


def clear_widget_cache(widget_id: UUID):
    _widget_cache.pop(str(widget_id), None)