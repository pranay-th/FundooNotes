from django.db import connection


def get_notes_with_label_count(user_id: int) -> list:
    """
    Raw SQL: notes with their label count for a user (non-trashed only).
    Uses parameterized query to prevent SQL injection.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                n.id,
                n.title,
                n.content,
                n.is_archived,
                n.is_trashed,
                n.created_at,
                COUNT(nl.label_id) AS label_count
            FROM notes n
            LEFT JOIN notes_labels nl ON nl.note_id = n.id
            WHERE n.created_by_id = %s
              AND n.is_trashed = FALSE
            GROUP BY n.id
            ORDER BY n.created_at DESC
            """,
            [user_id],
        )
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_notes_aggregation_stats(user_id: int) -> dict:
    """
    Raw SQL: total, archived, and trashed note counts for a user.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                COUNT(*)                                    AS total_notes,
                COUNT(*) FILTER (WHERE is_archived = TRUE) AS archived_count,
                COUNT(*) FILTER (WHERE is_trashed  = TRUE) AS trashed_count
            FROM notes
            WHERE created_by_id = %s
            """,
            [user_id],
        )
        row = cursor.fetchone()
        return {
            "total_notes":    row[0],
            "archived_count": row[1],
            "trashed_count":  row[2],
        }


def search_notes_raw(user_id: int, query: str) -> list:
    """
    Raw SQL: full-text ILIKE search on title and content.
    Uses parameterized query — query string is never interpolated.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                n.id,
                n.title,
                n.content,
                n.is_archived,
                n.is_trashed,
                n.created_at
            FROM notes n
            WHERE n.created_by_id = %s
              AND n.is_trashed = FALSE
              AND (n.title ILIKE %s OR n.content ILIKE %s)
            ORDER BY n.created_at DESC
            """,
            [user_id, f"%{query}%", f"%{query}%"],
        )
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
