"""
Tool executor — maps LLM tool-call names to real Django ORM operations.

Operates directly on the database rather than making internal HTTP calls,
so there is no networking overhead and no authentication token juggling.
"""

import json
from django.core.cache import cache
from django.db import connection
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

    if tool_name == "set_reminder":
        note_id = args.get("note_id")
        reminder_at = args.get("reminder_at")  # ISO string or None
        if not note_id:
            raise ToolExecutionError("note_id is required for set_reminder")
        try:
            note = Note.objects.get(pk=note_id, created_by=user)
        except Note.DoesNotExist:
            raise ToolExecutionError(f"Note {note_id} not found or not owned by you")

        if reminder_at is None:
            note.reminder_at = None
            note.save(update_fields=["reminder_at"])
            return {"reminder_cleared": True, "note_id": note_id}

        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        parsed = parse_datetime(reminder_at)
        if parsed is None:
            raise ToolExecutionError(
                f"Could not parse datetime '{reminder_at}'. Use ISO 8601 format, e.g. 2026-06-10T09:00:00"
            )
        if timezone.is_naive(parsed):
            parsed = timezone.make_aware(parsed)

        note.reminder_at = parsed
        note.save(update_fields=["reminder_at"])
        cache.delete(f"notes_list_{user.id}")
        return {
            "reminder_set": True,
            "note_id": note_id,
            "reminder_at": parsed.isoformat(),
        }

    if tool_name == "synthesize_notes":
        note_ids = args.get("note_ids", [])
        output_title = args.get("output_title", "Synthesis")
        instruction = args.get("instruction", "Summarise the key points from all provided notes.")

        if not note_ids:
            raise ToolExecutionError("note_ids must be a non-empty list")

        source_notes = Note.objects.filter(
            pk__in=note_ids, created_by=user, is_trashed=False
        ).prefetch_related("labels")

        if not source_notes.exists():
            raise ToolExecutionError("None of the specified notes were found")

        # Build the synthesis prompt and call OpenRouter inline
        notes_block = "\n\n".join(
            f"### {n.title or 'Untitled'} (id={n.pk})\n{n.content or '(empty)'}"
            for n in source_notes
        )
        synthesis_prompt = (
            f"{instruction}\n\n"
            f"Notes to synthesise:\n\n{notes_block}"
        )

        # Use the same OpenRouter call as views.py — import lazily to avoid circular imports
        import requests as req
        from decouple import config
        api_key = config("CHATBOT_OPENROUTER_API_KEY", default="")
        resp = req.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that synthesises notes."},
                    {"role": "user", "content": synthesis_prompt},
                ],
            },
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=60,
        )
        resp.raise_for_status()
        synthesised_content = resp.json()["choices"][0]["message"]["content"]

        # Create the new note with the synthesised content
        new_note = Note.objects.create(
            created_by=user,
            title=output_title,
            content=synthesised_content,
            color="default",
        )
        cache.delete(f"notes_list_{user.id}")
        return {
            "synthesised": True,
            "created_note_id": new_note.pk,
            "title": output_title,
            "source_note_ids": note_ids,
        }

    if tool_name == "organise_notes_by_topic":
        # Get all active notes
        notes = list(
            Note.objects.filter(created_by=user, is_trashed=False)
            .prefetch_related("labels")
            .order_by("-updated_at")
        )
        if not notes:
            return {"message": "No notes to organise."}

        # Ask the LLM to categorise the notes
        notes_block = "\n".join(
            f"- [id={n.pk}] {n.title or 'Untitled'}: {(n.content or '')[:150]}"
            for n in notes
        )
        categorise_prompt = (
            "Analyse these notes and group them by topic. "
            "Return a JSON object where keys are topic names (short, 1-3 words) "
            "and values are arrays of note IDs. "
            "Every note ID must appear in exactly one topic.\n\n"
            f"Notes:\n{notes_block}"
        )

        import requests as req
        from decouple import config
        api_key = config("CHATBOT_OPENROUTER_API_KEY", default="")
        resp = req.post(
            "https://openrouter.ai/api/v1/chat/completions",
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a helpful organiser. Always respond with valid JSON only, no markdown."},
                    {"role": "user", "content": categorise_prompt},
                ],
                "response_format": {"type": "json_object"},
            },
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=60,
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]

        try:
            topic_map = json.loads(raw)  # { "Topic Name": [id1, id2, ...], ... }
        except json.JSONDecodeError:
            raise ToolExecutionError("Could not parse topic grouping from AI response")

        created_labels = {}
        assigned = 0

        for topic_name, note_id_list in topic_map.items():
            topic_name = topic_name.strip()
            if not topic_name or not note_id_list:
                continue

            # Create or get the label
            label, _ = Label.objects.get_or_create(
                title=topic_name, created_by=user
            )
            created_labels[topic_name] = label.pk

            # Assign label to each note in this topic
            for nid in note_id_list:
                try:
                    note = Note.objects.get(pk=nid, created_by=user, is_trashed=False)
                    note.labels.add(label)
                    assigned += 1
                except Note.DoesNotExist:
                    continue

        cache.delete(f"notes_list_{user.id}")
        return {
            "organised": True,
            "topics_created": list(created_labels.keys()),
            "notes_assigned": assigned,
        }

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

    # ── Collaboration ─────────────────────────────────────────────────────

    if tool_name == "list_shared_notes":
        # Query the note_collaborators table directly (same DB, owned by collab service)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT n.id, n.title, n.content, n.color, nc.access_level
                FROM note_collaborators nc
                JOIN notes n ON nc.note_id = n.id
                WHERE nc.collaborator_id = %s AND n.is_trashed = false
                ORDER BY nc.created_at DESC
                """,
                [user.id],
            )
            cols = [col[0] for col in cursor.description]
            rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
        return {"shared_notes": rows}

    raise ToolExecutionError(f"Unknown tool: {tool_name}")
