"""
OpenAI-style tool definitions for the FundooNotes AI agent.
These are passed to the LLM so it can call backend APIs on the user's behalf.
"""

TOOLS = [
    # ── Notes ─────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "list_notes",
            "description": "List all of the user's own notes (excluding trashed ones).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Create a new note for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title":   {"type": "string", "description": "Note title"},
                    "content": {"type": "string", "description": "Note body / content"},
                    "color":   {
                        "type": "string",
                        "description": "Optional color key: default, red, orange, yellow, green, teal, blue, purple, pink, brown, gray",
                        "default": "default",
                    },
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_note",
            "description": "Update an existing note by its numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id":     {"type": "integer", "description": "The note's numeric ID"},
                    "title":       {"type": "string",  "description": "New title (optional)"},
                    "content":     {"type": "string",  "description": "New content (optional)"},
                    "color":       {"type": "string",  "description": "New color key (optional)"},
                    "is_archived": {"type": "boolean", "description": "Archive or unarchive"},
                    "is_trashed":  {"type": "boolean", "description": "Trash or restore"},
                },
                "required": ["note_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_note",
            "description": "Move a note to trash by its numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id": {"type": "integer", "description": "The note's numeric ID"},
                },
                "required": ["note_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "synthesize_notes",
            "description": (
                "Read the content of multiple notes and create a new summary/synthesis note "
                "combining their key points. Use this when the user asks to summarise, combine, "
                "or create a document from multiple notes."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "note_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of note IDs to synthesise",
                    },
                    "output_title": {
                        "type": "string",
                        "description": "Title for the new synthesised note",
                    },
                    "instruction": {
                        "type": "string",
                        "description": "How to combine them, e.g. 'create a bullet-point summary' or 'write a narrative overview'",
                        "default": "Summarise the key points from all provided notes.",
                    },
                },
                "required": ["note_ids", "output_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": (
                "Set a reminder on a note. The user will receive an email at the specified time. "
                "Pass the datetime as an ISO 8601 string, e.g. '2026-06-10T09:00:00'. "
                "Pass null to clear an existing reminder."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id":     {"type": "integer", "description": "The note's numeric ID"},
                    "reminder_at": {
                        "type": ["string", "null"],
                        "description": "ISO 8601 datetime string for when to send the reminder, or null to clear",
                    },
                },
                "required": ["note_id", "reminder_at"],
            },
        },
    },
    # ── Labels ────────────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "list_labels",
            "description": "List all labels belonging to the user.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_label",
            "description": "Create a new label.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Label name"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_label",
            "description": "Rename an existing label by its numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "label_id": {"type": "integer", "description": "The label's numeric ID"},
                    "title":    {"type": "string",  "description": "New label name"},
                },
                "required": ["label_id", "title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_label",
            "description": "Delete a label by its numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "label_id": {"type": "integer", "description": "The label's numeric ID"},
                },
                "required": ["label_id"],
            },
        },
    },
    # ── Collaboration ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "list_shared_notes",
            "description": "List all notes that have been shared with the user by other people.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    # ── Organisation ─────────────────────────────────────────────────────────
    {
        "type": "function",
        "function": {
            "name": "organise_notes_by_topic",
            "description": (
                "Analyse all the user's notes, group them by topic, and create a label for each "
                "topic. Then assign the relevant label to each note. Use this when the user asks "
                "to organise or categorise their notes."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]
