"""
SQLAlchemy ORM models for the Note Collaboration Service.

Design notes
------------
* ``User`` and ``Note`` are **read-only mirrors** of the tables owned by the
  Django backend.  The Collaboration Service never inserts or updates rows in
  those tables; it only reads them.
* ``NoteCollaborator`` is the only table **owned** by this service and managed
  via Alembic migrations.
* Relationships are defined so that SQLAlchemy can join across tables in a
  single async query without triggering lazy-load errors.
"""

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


# ---------------------------------------------------------------------------
# Declarative base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Read-only mirror: users table (owned by Django)
# ---------------------------------------------------------------------------

class User(Base):
    """
    Read-only mirror of Django's ``users`` table.

    Only the columns needed by the Collaboration Service are mapped here.
    Additional Django columns (password, phone_number, etc.) are intentionally
    omitted — SQLAlchemy will simply ignore them when reading rows.
    """

    __tablename__ = "users"

    id          = Column(BigInteger, primary_key=True)
    username    = Column(String(150), nullable=False)
    email       = Column(String(254), unique=True, nullable=False)
    is_active   = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r}>"


# ---------------------------------------------------------------------------
# Read-only mirror: notes table (owned by Django)
# ---------------------------------------------------------------------------

class Note(Base):
    """
    Read-only mirror of Django's ``notes`` table.

    The ``collaborators`` relationship allows the service to load all
    ``NoteCollaborator`` records for a note in a single joined query.
    The ``cascade="all, delete-orphan"`` setting is intentionally omitted
    here because cascade deletes are enforced at the database level (FK
    ``ON DELETE CASCADE`` in the Alembic migration); SQLAlchemy-level cascade
    would require the service to own the ``notes`` table, which it does not.
    """

    __tablename__ = "notes"

    id            = Column(BigInteger, primary_key=True)
    title         = Column(String(255), nullable=False)
    content       = Column(Text, default="")
    color         = Column(String(20), default="default")
    is_archived   = Column(Boolean, default=False)
    is_trashed    = Column(Boolean, default=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # One note → many collaborator records
    collaborators = relationship(
        "NoteCollaborator",
        back_populates="note",
        lazy="select",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Note id={self.id} title={self.title!r}>"


# ---------------------------------------------------------------------------
# Owned table: note_collaborators (managed by Alembic)
# ---------------------------------------------------------------------------

class NoteCollaborator(Base):
    """
    Represents an invitation that grants a registered user access to a note
    they do not own.

    Constraints
    -----------
    * ``uq_note_collaborator`` — a user can only be invited once per note;
      a second invite updates the existing record's ``access_level`` instead
      of inserting a duplicate row.
    * ``ck_access_level`` — only ``'read'`` and ``'read_write'`` are valid
      access levels; enforced at the DB level as well as via Pydantic schemas.
    """

    __tablename__ = "note_collaborators"
    __table_args__ = (
        UniqueConstraint("note_id", "collaborator_id", name="uq_note_collaborator"),
        CheckConstraint(
            "access_level IN ('read', 'read_write')",
            name="ck_access_level",
        ),
    )

    id              = Column(BigInteger, primary_key=True, autoincrement=True)
    note_id         = Column(
        BigInteger,
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    collaborator_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    access_level    = Column(String(10), nullable=False)   # "read" | "read_write"
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    note         = relationship("Note", back_populates="collaborators")
    collaborator = relationship("User")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<NoteCollaborator note_id={self.note_id} "
            f"collaborator_id={self.collaborator_id} "
            f"access_level={self.access_level!r}>"
        )
