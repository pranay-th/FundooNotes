"""
Collaborator-management endpoints for the Note Collaboration Service.

All four endpoints are owner-only operations — they require the authenticated
user to be the note owner (enforced via the ``require_note_owner`` dependency).

Routes
------
POST   /notes/{note_id}/collaborators              — invite a collaborator
GET    /notes/{note_id}/collaborators              — list collaborators
PATCH  /notes/{note_id}/collaborators/{user_id}   — update access level
DELETE /notes/{note_id}/collaborators/{user_id}   — remove a collaborator
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import TokenPayload, get_current_user
from app.database import get_db
from app.dependencies import require_note_owner
from app.models import Note, NoteCollaborator, User
from app.schemas import CollaboratorOut, InviteRequest, UpdateAccessRequest

router = APIRouter(prefix="/notes", tags=["collaborators"])


# ---------------------------------------------------------------------------
# Helper: build a CollaboratorOut from a NoteCollaborator + User pair
# ---------------------------------------------------------------------------

def _collaborator_out(record: NoteCollaborator, user: User) -> CollaboratorOut:
    """Map ORM objects to the response schema."""
    return CollaboratorOut(
        user_id=user.id,
        username=user.username,
        email=user.email,
        access_level=record.access_level,
        created_at=record.created_at,
    )


# ---------------------------------------------------------------------------
# POST /notes/{note_id}/collaborators — invite a collaborator
# ---------------------------------------------------------------------------

@router.post(
    "/{note_id}/collaborators",
    response_model=CollaboratorOut,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a collaborator",
)
async def invite_collaborator(
    note_id: int,
    body: InviteRequest,
    note: Note = Depends(require_note_owner),
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CollaboratorOut:
    """
    Invite a registered user to collaborate on a note.

    - Looks up the target user by email (404 if not found).
    - Rejects self-invitations (400).
    - If the user is already a collaborator, updates the access level (upsert).
    - Returns the collaborator record with HTTP 201.

    Requires: authenticated user must be the note owner.
    """
    # Look up the target user by email
    result = await db.execute(
        select(User).where(User.email == body.collaborator_email)
    )
    target_user = result.scalar_one_or_none()

    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user found with email '{body.collaborator_email}'.",
        )

    # Reject self-invitation
    if target_user.id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot invite yourself as a collaborator.",
        )

    # Check for an existing collaborator record (upsert logic)
    existing_result = await db.execute(
        select(NoteCollaborator).where(
            NoteCollaborator.note_id == note_id,
            NoteCollaborator.collaborator_id == target_user.id,
        )
    )
    existing = existing_result.scalar_one_or_none()

    if existing is not None:
        # Update the access level on the existing record
        existing.access_level = body.access_level.value
        await db.commit()
        await db.refresh(existing)
        return _collaborator_out(existing, target_user)

    # Create a new collaborator record
    new_record = NoteCollaborator(
        note_id=note_id,
        collaborator_id=target_user.id,
        access_level=body.access_level.value,
    )
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    return _collaborator_out(new_record, target_user)


# ---------------------------------------------------------------------------
# GET /notes/{note_id}/collaborators — list collaborators
# ---------------------------------------------------------------------------

@router.get(
    "/{note_id}/collaborators",
    response_model=list[CollaboratorOut],
    summary="List collaborators on a note",
)
async def list_collaborators(
    note_id: int,
    note: Note = Depends(require_note_owner),
    db: AsyncSession = Depends(get_db),
) -> list[CollaboratorOut]:
    """
    Return all collaborators on a note, each with their user details and
    access level.

    Returns an empty list when the note has no collaborators.

    Requires: authenticated user must be the note owner.
    """
    result = await db.execute(
        select(NoteCollaborator, User)
        .join(User, NoteCollaborator.collaborator_id == User.id)
        .where(NoteCollaborator.note_id == note_id)
        .order_by(NoteCollaborator.created_at)
    )
    rows = result.all()

    return [_collaborator_out(record, user) for record, user in rows]


# ---------------------------------------------------------------------------
# PATCH /notes/{note_id}/collaborators/{user_id} — update access level
# ---------------------------------------------------------------------------

@router.patch(
    "/{note_id}/collaborators/{user_id}",
    response_model=CollaboratorOut,
    summary="Update a collaborator's access level",
)
async def update_collaborator(
    note_id: int,
    user_id: int,
    body: UpdateAccessRequest,
    note: Note = Depends(require_note_owner),
    db: AsyncSession = Depends(get_db),
) -> CollaboratorOut:
    """
    Change the access level of an existing collaborator on a note.

    Raises HTTP 404 if the specified user is not a collaborator on this note.

    Requires: authenticated user must be the note owner.
    """
    # Fetch the collaborator record
    result = await db.execute(
        select(NoteCollaborator, User)
        .join(User, NoteCollaborator.collaborator_id == User.id)
        .where(
            NoteCollaborator.note_id == note_id,
            NoteCollaborator.collaborator_id == user_id,
        )
    )
    row = result.one_or_none()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborator not found on this note.",
        )

    record, user = row
    record.access_level = body.access_level.value
    await db.commit()
    await db.refresh(record)

    return _collaborator_out(record, user)


# ---------------------------------------------------------------------------
# DELETE /notes/{note_id}/collaborators/{user_id} — remove a collaborator
# ---------------------------------------------------------------------------

@router.delete(
    "/{note_id}/collaborators/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a collaborator from a note",
)
async def remove_collaborator(
    note_id: int,
    user_id: int,
    note: Note = Depends(require_note_owner),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Remove a collaborator from a note, revoking their access.

    Raises HTTP 404 if the specified user is not a collaborator on this note.

    Requires: authenticated user must be the note owner.
    """
    result = await db.execute(
        select(NoteCollaborator).where(
            NoteCollaborator.note_id == note_id,
            NoteCollaborator.collaborator_id == user_id,
        )
    )
    record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaborator not found on this note.",
        )

    await db.delete(record)
    await db.commit()
