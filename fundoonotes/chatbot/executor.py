"""
Tool executor — maps LLM tool-call names to real Django ORM operations.

Operates directly on the database rather than making internal HTTP calls,
so there is no networking overhead and no authentication token juggling.
"""

import json
from django.core.cache import cache
from notes.models import Note
from notes.serializers import NoteSerializer
from labels.models import Label
from labels.serializers import LabelSerializer


class ToolExecutionError(Exception):
    pass


def execute_tool(tool_name: str, arguments: dict, user) -> str:
    """
    Dispatch a tool call and return the result as a JSON string
    (fed back to the LLM as a tool-role message).
    """
    try:
        result = _dispatch(tool_name, arguments, user)
        return json.dumps(result)
    except ToolExecutionError as exc:
        return json.dumps({"error": str(exc)})
    except Exception as exc:
        return json.dumps({"error": f"Unexpected error in {tool_name}: {str(exc)}"})


def _dispatch(tool_name: str, args: dict, user) -> dict:  # noqa: C901
    # ── Notes ─────────────────────────────────────────────────────────────

    if tool_name == "list_notes":
        notes = (
            Note.objects.filter(created_by=user, is_trashed=False)
            .prefetch_related("labels")
            .order_by("-updated_at")
        )
        return {"notes": NoteSerializer(notes, many=True).data}

    if tool_name == "create_note":
        note = Note.objects.create(
            created_by=user,
            title=args.get("title", ""),
            content=args.get("content", ""),
            color=args.get("color", "default"),
        )
        cache.delete(f"notes_list_{user.id}")
        return {"created": NoteSerializer(note).data}

    if tool_name == "update_note":
        note_id = args.get("note_id")
        if not note_id:
            raise ToolExecutionError("note_id is required for update_note")
        try:
            note = Note.objects.get(pk=note_id, created_by=user)
        except Note.DoesNotExist:
            raise ToolExecutionError(f"Note {note_id} not found or not owned by you")

        for field in ("title", "content", "color", "is_archived", "is_trashed"):
            if field in args:
                setattr(note, field, args[field])
        note.save()
        cache.delete(f"notes_list_{user.id}")
        cache.delete(f"note_detail_{note.id}")
        return {"updated": NoteSerializer(note).data}

    if tool_name == "delete_note":
        note_id = args.get("note_id")
        if not note_id:
            raise ToolExecutionError("note_id is required for delete_note")
        try:
            note = Note.objects.get(pk=note_id, created_by=user)
        except Note.DoesNotExist:
            raise ToolExecutionError(f"Note {note_id} not found or not owned by you")
        note.is_trashed = True
        note.save(update_fields=["is_trashed", "updated_at"])
        cache.delete(f"notes_list_{user.id}")
        cache.delete(f"note_detail_{note.id}")
        return {"deleted": True, "note_id": note_id}

    # ── Labels ────────────────────────────────────────────────────────────

    if tool_name == "list_labels":
        labels = Label.objects.filter(created_by=user)
        return {"labels": LabelSerializer(labels, many=True).data}

    if tool_name == "create_label":
        title = args.get("title", "").strip()
        if not title:
            raise ToolExecutionError("title is required for create_label")
        label = Label.objects.create(created_by=user, title=title)
        return {"created": LabelSerializer(label).data}

    if tool_name == "update_label":
        label_id = args.get("label_id")
        title = args.get("title", "").strip()
        if not label_id or not title:
            raise ToolExecutionError("label_id and title are required for update_label")
        try:
            label = Label.objects.get(pk=label_id, created_by=user)
        except Label.DoesNotExist:
            raise ToolExecutionError(f"Label {label_id} not found or not owned by you")
        label.title = title
        label.save()
        return {"updated": LabelSerializer(label).data}

    if tool_name == "delete_label":
        label_id = args.get("label_id")
        if not label_id:
            raise ToolExecutionError("label_id is required for delete_label")
        try:
            label = Label.objects.get(pk=label_id, created_by=user)
        except Label.DoesNotExist:
            raise ToolExecutionError(f"Label {label_id} not found or not owned by you")
        label.delete()
        return {"deleted": True, "label_id": label_id}

    raise ToolExecutionError(f"Unknown tool: {tool_name}")
