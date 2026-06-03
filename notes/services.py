from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import Note


def get_notes_for_user(user_id: int):
    """
    Returns non-trashed notes for the given user.
    Checks Redis cache first; populates on miss with TTL=300s.
    """
    cache_key = f"notes_list_{user_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    notes = (
        Note.objects.filter(created_by_id=user_id, is_trashed=False)
        .select_related("created_by")
        .prefetch_related("labels")
    )
    # Evaluate queryset before caching
    notes = list(notes)
    cache.set(cache_key, notes, timeout=300)
    return notes


def create_note(user, validated_data: dict) -> Note:
    """
    Creates a note owned by `user`.
    Validates that all supplied labels are owned by the user.
    Invalidates the user's notes list cache.
    """
    label_ids = validated_data.pop("label_ids", [])

    # Validate label ownership
    for label in label_ids:
        if label.created_by != user:
            raise ValidationError(
                f"Label '{label.title}' does not belong to you."
            )

    note = Note.objects.create(created_by=user, **validated_data)
    if label_ids:
        note.labels.set(label_ids)

    cache.delete(f"notes_list_{user.id}")
    return note


def get_note_or_403(note_id: int, user) -> Note:
    """
    Returns the note if it exists and belongs to `user`.
    Raises 404 if not found, 403 if not owner.
    """
    note = get_object_or_404(Note, pk=note_id)
    if note.created_by != user:
        raise PermissionDenied("You do not have permission to access this note.")
    return note


def update_note(note: Note, validated_data: dict, partial: bool = False) -> Note:
    """
    Updates note fields and optionally replaces labels.
    Invalidates list and detail caches.
    """
    label_ids = validated_data.pop("label_ids", None)

    for field, value in validated_data.items():
        setattr(note, field, value)
    note.save()

    if label_ids is not None:
        # Validate ownership
        for label in label_ids:
            if label.created_by != note.created_by:
                raise ValidationError(
                    f"Label '{label.title}' does not belong to you."
                )
        note.labels.set(label_ids)

    cache.delete(f"notes_list_{note.created_by_id}")
    cache.delete(f"note_detail_{note.id}")
    return note


def delete_note(note: Note) -> None:
    """
    Soft-deletes a note by setting is_trashed=True.
    Invalidates list and detail caches.
    """
    note.is_trashed = True
    note.save(update_fields=["is_trashed", "updated_at"])
    cache.delete(f"notes_list_{note.created_by_id}")
    cache.delete(f"note_detail_{note.id}")
