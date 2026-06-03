"""
Note-access endpoints for the Note Collaboration Service.

These endpoints allow collaborators to read and (if permitted) update shared
notes.  Access is gated by the ``require_collaborator`` dependency, which
returns the caller's ``NoteCollaborator`` record.  Write operations are
further restricted to ``read_write`` collaborators.

Collaborator-management operations (invite, remove, list, update access level)
live on a separate router (``collaborators.py``) that uses
``require_note_owner``, so they are unreachable from this router — satisfying
requirements 6.4 and 6.5 by routing alone.

Routes
------
GET   /notes/{note_id}/content  — read a shared note (read or read_write)
PATCH /notes/{note_id}/content  — update a shared note (read_write only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import require_collaborator
from app.models import Note, NoteCollaborator
from app.schemas import NoteOut, NoteUpdateRequest

router = APIRouter(prefix="/notes", tags=["note-access"])


# ---------------------------------------------------------------------------
# GET /notes/{note_id}/content — read a shared note
# ---------------------------------------------------------------------------

@router.get(
    "/{note_id}/content",
    response_model=NoteOut,
    summary="Read a shared note",
)
async def get_note_content(
    note_id: int,
    collab_record: NoteCollaborator = Depends(require_collaborator),
    db: AsyncSession = Depends(get_db),
) -> NoteOut:
    """
    Return the content of a note shared with the authenticated user.

    Both ``read`` and ``read_write`` collaborators are permitted.

    Raises:
        HTTP 403 — caller is not a collaborator on this note (raised by
                   ``require_collaborator`` before this handler runs).
        HTTP 404 — note not found (should not occur in practice if FK
                   constraints are intact, but handled defensively).

    Requirements: 6.1
    """
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )

    return NoteOut(
        id=note.id,
        title=note.title,
        content=note.content,
        color=note.color,
        updated_at=note.updated_at,
    )


# ---------------------------------------------------------------------------
# PATCH /notes/{note_id}/content — update a shared note
# ---------------------------------------------------------------------------

@router.patch(
    "/{note_id}/content",
    response_model=NoteOut,
    summary="Update a shared note",
)
async def update_note_content(
    note_id: int,
    body: NoteUpdateRequest,
    collab_record: NoteCollaborator = Depends(require_collaborator),
    db: AsyncSession = Depends(get_db),
) -> NoteOut:
    """
    Apply a partial update to a shared note.

    Only ``read_write`` collaborators may call this endpoint.  A ``read``
    collaborator receives HTTP 403.

    Only fields explicitly provided in the request body (non-``None`` values)
    are applied to the note record.  Fields omitted from the request are left
    unchanged.

    Raises:
        HTTP 403 — caller is not a collaborator (``require_collaborator``).
        HTTP 403 — collaborator has ``read`` access level.
        HTTP 404 — note not found.

    Requirements: 6.2, 6.3
    """
    # Enforce write permission
    if collab_record.access_level == "read":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Read-only access. You do not have permission to modify this note.",
        )

    # Fetch the note
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found.",
        )

    # Apply partial update — skip fields that were not provided (None)
    for field, value in body.model_dump().items():
        if value is not None:
            setattr(note, field, value)

    await db.commit()
    await db.refresh(note)

    return NoteOut(
        id=note.id,
        title=note.title,
        content=note.content,
        color=note.color,
        updated_at=note.updated_at,
    )
