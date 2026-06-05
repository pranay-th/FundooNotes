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
            "description": "List all of the user's notes (excluding trashed ones).",
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
                    "note_id": {"type": "integer", "description": "The note's numeric ID"},
                    "title":   {"type": "string",  "description": "New title (optional)"},
                    "content": {"type": "string",  "description": "New content (optional)"},
                    "color":   {"type": "string",  "description": "New color key (optional)"},
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
]
