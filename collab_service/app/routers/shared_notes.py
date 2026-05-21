"""
Shared-notes endpoint for the Note Collaboration Service.

Returns all notes that have been shared with the authenticated user —
i.e. notes for which a ``NoteCollaborator`` record exists with the current
user as the collaborator, excluding any notes that have been trashed.

Routes
------
GET /notes/shared — list notes shared with the authenticated user
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import TokenPayload, get_current_user
from app.database import get_db
from app.models import Note, NoteCollaborator
from app.schemas import AccessLevel, SharedNoteOut

router = APIRouter(prefix="/notes", tags=["shared-notes"])


# ---------------------------------------------------------------------------
# GET /notes/shared — list notes shared with the authenticated user
# ---------------------------------------------------------------------------

@router.get(
    "/shared",
    response_model=list[SharedNoteOut],
    summary="List notes shared with the authenticated user",
)
async def list_shared_notes(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[SharedNoteOut]:
    """
    Return all notes shared with the authenticated user.

    A note is considered "shared" when a ``NoteCollaborator`` record exists
    linking the current user (as collaborator) to that note.  Notes that have
    been trashed (``is_trashed = True``) are excluded from the results.

    Returns an empty list with HTTP 200 when the user has no shared notes.

    Requirements: 5.1, 5.2, 5.3
    """
    result = await db.execute(
        select(NoteCollaborator, Note)
        .join(Note, NoteCollaborator.note_id == Note.id)
        .where(
            NoteCollaborator.collaborator_id == current_user.user_id,
            Note.is_trashed == False,  # noqa: E712 — SQLAlchemy requires == not `is`
        )
        .order_by(NoteCollaborator.created_at)
    )
    rows = result.all()

    return [
        SharedNoteOut(
            id=note.id,
            title=note.title,
            content=note.content,
            color=note.color,
            access_level=AccessLevel(collab.access_level),
        )
        for collab, note in rows
    ]
