"""
Reusable FastAPI dependencies for the Note Collaboration Service.

These dependencies enforce ownership and collaboration access rules,
centralising the 403/404 logic so individual route handlers stay clean.
"""

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import TokenPayload, get_current_user
from app.database import get_db
from app.models import Note, NoteCollaborator


async def require_note_owner(
    note_id: int,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Note:
    """
    Return the note if ``current_user`` is the owner; raise an HTTP error otherwise.

    Raises:
        HTTP 404 — note not found.
        HTTP 403 — authenticated user is not the note owner.
    """
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()

    if note is None:
        raise HTTPException(status_code=404, detail="Note not found.")

    if note.created_by_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to manage this note.",
        )

    return note


async def require_collaborator(
    note_id: int,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NoteCollaborator:
    """
    Return the ``NoteCollaborator`` record for the current user on the given note.

    Raises:
        HTTP 403 — authenticated user is not a collaborator on this note.
    """
    result = await db.execute(
        select(NoteCollaborator).where(
            NoteCollaborator.note_id == note_id,
            NoteCollaborator.collaborator_id == current_user.user_id,
        )
    )
    collaborator = result.scalar_one_or_none()

    if collaborator is None:
        raise HTTPException(
            status_code=403,
            detail="You are not a collaborator on this note.",
        )

    return collaborator
