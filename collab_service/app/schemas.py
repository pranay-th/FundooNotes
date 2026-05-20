from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr


class AccessLevel(str, Enum):
    read       = "read"
    read_write = "read_write"


# --- Requests ---

class InviteRequest(BaseModel):
    collaborator_email: EmailStr
    access_level: AccessLevel


class UpdateAccessRequest(BaseModel):
    access_level: AccessLevel


class NoteUpdateRequest(BaseModel):
    title:   str | None = None
    content: str | None = None
    color:   str | None = None


# --- Responses ---

class CollaboratorOut(BaseModel):
    user_id:      int
    username:     str
    email:        str
    access_level: AccessLevel
    created_at:   datetime

    model_config = {"from_attributes": True}


class SharedNoteOut(BaseModel):
    id:           int
    title:        str
    content:      str
    color:        str
    access_level: AccessLevel

    model_config = {"from_attributes": True}


class NoteOut(BaseModel):
    id:         int
    title:      str
    content:    str
    color:      str
    updated_at: datetime

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status:   str   # "ok" | "degraded"
    database: str   # "reachable" | "unreachable"
