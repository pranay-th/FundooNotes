"""create note_collaborators table

Revision ID: 0001
Revises:
Create Date: 2026-05-19

This migration creates the ``note_collaborators`` table, which is the only
table owned by the Note Collaboration Service.  The ``notes`` and ``users``
tables are owned by the Django backend and are referenced here only via
foreign-key constraints.
"""

from alembic import op
import sqlalchemy as sa

# ---------------------------------------------------------------------------
# Revision identifiers — used by Alembic
# ---------------------------------------------------------------------------
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


# ---------------------------------------------------------------------------
# Upgrade: create the table
# ---------------------------------------------------------------------------

def upgrade() -> None:
    op.create_table(
        "note_collaborators",
        # Primary key
        sa.Column(
            "id",
            sa.BigInteger(),
            primary_key=True,
            autoincrement=True,
            nullable=False,
        ),
        # Foreign key → notes.id  (ON DELETE CASCADE)
        sa.Column("note_id", sa.BigInteger(), nullable=False),
        # Foreign key → users.id  (ON DELETE CASCADE)
        sa.Column("collaborator_id", sa.BigInteger(), nullable=False),
        # Access level: only 'read' or 'read_write' are valid
        sa.Column("access_level", sa.String(10), nullable=False),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        # Foreign-key constraints with cascade deletes
        sa.ForeignKeyConstraint(
            ["note_id"],
            ["notes.id"],
            name="fk_nc_note_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["collaborator_id"],
            ["users.id"],
            name="fk_nc_collaborator_id",
            ondelete="CASCADE",
        ),
        # Unique constraint: a user can only be invited once per note
        sa.UniqueConstraint(
            "note_id",
            "collaborator_id",
            name="uq_note_collaborator",
        ),
        # Check constraint: only valid access levels are stored
        sa.CheckConstraint(
            "access_level IN ('read', 'read_write')",
            name="ck_access_level",
        ),
    )

    # Index on note_id for fast collaborator lookups per note
    op.create_index(
        "ix_nc_note_id",
        "note_collaborators",
        ["note_id"],
    )

    # Index on collaborator_id for fast shared-notes lookups per user
    op.create_index(
        "ix_nc_collaborator_id",
        "note_collaborators",
        ["collaborator_id"],
    )


# ---------------------------------------------------------------------------
# Downgrade: drop the table (indexes are dropped automatically)
# ---------------------------------------------------------------------------

def downgrade() -> None:
    op.drop_table("note_collaborators")
