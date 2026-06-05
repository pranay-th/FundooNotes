"""
Chatbot views — agentic tool-calling loop + SSE streaming.

Flow for POST /api/chatbot/chat/:
  1. Build system prompt with user's current notes injected.
  2. Send messages + TOOLS to OpenRouter (non-streaming) with tool_choice=auto.
  3. If the model returns tool_calls, execute them via executor.py and loop.
  4. Once the model returns a plain text reply (no tool calls), stream it
     back to the frontend token-by-token via SSE.

This means the LLM can actually CREATE / EDIT / DELETE notes and labels,
not just talk about doing it.
"""

import json
import requests
from decouple import config
from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from notes.models import Note
from .tools import TOOLS
from .executor import execute_tool

OPENROUTER_API_KEY = config("CHATBOT_OPENROUTER_API_KEY", default="")
OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
# Use a model that supports tool/function calling
MODEL = "openai/gpt-4o-mini"

MAX_TOOL_ITERATIONS = 10

BASE_SYSTEM_PROMPT = (
    "You are a helpful AI assistant embedded in FundooNotes, a note-taking app. "
    "You have access to tools that let you CREATE, READ, UPDATE, and DELETE the "
    "user's notes and labels, set reminders, synthesise multiple notes into one, "
    "organise notes by topic, and list notes shared with the user. "
    "USE THE TOOLS when the user asks you to do something. "
    "Do not describe what you are going to do; just call the tool and report the result concisely. "
    "When setting reminders, always confirm the exact date and time back to the user. "
    "The user's current notes are listed below for reference.\n\n"
    "{notes_context}"
    "{shared_context}"
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_system_prompt(user) -> str:
    notes = Note.objects.filter(
        created_by=user, is_trashed=False
    ).order_by("-updated_at")[:20]

    if notes:
        lines = []
        for n in notes:
            title   = (n.title   or "Untitled").strip()
            content = (n.content or "").strip()[:300]
            reminder = f" [reminder: {n.reminder_at.isoformat()}]" if n.reminder_at else ""
            entry   = f"- [id={n.pk}] [{title}]{reminder}"
            if content:
                entry += f": {content}"
            lines.append(entry)
        notes_context = "User's own notes (include id when calling update/delete/reminder tools):\n" + "\n".join(lines)
    else:
        notes_context = "The user has no notes yet."

    # Also inject shared notes so the AI can answer questions about them
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT n.id, n.title, n.content, nc.access_level
                FROM note_collaborators nc
                JOIN notes n ON nc.note_id = n.id
                WHERE nc.collaborator_id = %s AND n.is_trashed = false
                ORDER BY nc.created_at DESC
                LIMIT 10
                """,
                [user.id],
            )
            shared_rows = cursor.fetchall()
        if shared_rows:
            shared_lines = [
                f"- [shared-id={row[0]}] [{row[1] or 'Untitled'}] ({row[3]}): {(row[2] or '')[:200]}"
                for row in shared_rows
            ]
            shared_context = "\n\nNotes shared with the user by others:\n" + "\n".join(shared_lines)
        else:
            shared_context = ""
    except Exception:
        shared_context = ""

    return BASE_SYSTEM_PROMPT.format(
        notes_context=notes_context,
        shared_context=shared_context,
    )


def _call_openrouter(messages: list, stream: bool = False, tools=None) -> requests.Response:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload: dict = {
        "model": MODEL,
        "messages": messages,
        "stream": stream,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    resp = requests.post(
        OPENROUTER_CHAT_URL,
        json=payload,
        headers=headers,
        timeout=60,
        stream=stream,
    )
    resp.raise_for_status()
    return resp


def _run_agentic_loop(messages: list, user) -> list:
    """
    Execute the tool-calling loop.
    Returns the full messages list with all tool calls + results appended,
    ending with the assistant's final text message.
    """
    for _ in range(MAX_TOOL_ITERATIONS):
        resp = _call_openrouter(messages, stream=False, tools=TOOLS)
        data = resp.json()
        choice = data["choices"][0]
        assistant_msg = choice["message"]

        # Append assistant turn to conversation
        messages.append(assistant_msg)

        # If no tool calls — we have the final answer
        tool_calls = assistant_msg.get("tool_calls")
        if not tool_calls:
            break

        # Execute each tool call and append results
        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            try:
                fn_args = json.loads(tc["function"].get("arguments", "{}"))
            except json.JSONDecodeError:
                fn_args = {}

            result = execute_tool(fn_name, fn_args, user)

            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": result,
            })

    return messages


def _stream_text(text: str):
    """
    Stream a known string as SSE tokens (word-by-word for a live feel).
    Ends with data: [DONE].
    """
    # Split into ~word-sized chunks so it looks like streaming
    words = text.split(" ")
    for i, word in enumerate(words):
        chunk = word if i == len(words) - 1 else word + " "
        yield f"data: {json.dumps(chunk)}\n\n"
    yield "data: [DONE]\n\n"


def _stream_from_openrouter(messages: list):
    """
    Stream the final assistant reply directly from OpenRouter token-by-token.
    Used when there are no tool calls needed.
    """
    try:
        resp = _call_openrouter(messages, stream=True)
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
            if not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if data == "[DONE]":
                yield "data: [DONE]\n\n"
                return
            try:
                chunk = json.loads(data)
                token = chunk["choices"][0]["delta"].get("content", "")
                if token:
                    yield f"data: {json.dumps(token)}\n\n"
            except (KeyError, json.JSONDecodeError):
                continue
    except Exception as exc:
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
    yield "data: [DONE]\n\n"


def _agentic_stream(messages: list, user):
    """
    Main generator:
      1. Run the agentic loop (tool calls, non-streaming).
      2. Stream the final text reply.
    Yields SSE events throughout.
    """
    try:
        # Phase 1: tool-calling loop (may perform DB writes)
        messages = _run_agentic_loop(messages, user)

        # The last message is the final assistant reply
        last = messages[-1]
        final_text = last.get("content") or ""

        if not final_text:
            yield f"data: {json.dumps({'error': 'No response from AI'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        # Phase 2: stream the final text word-by-word
        yield from _stream_text(final_text)

    except requests.exceptions.ConnectionError:
        yield f"data: {json.dumps({'error': 'Cannot reach the AI service. Check your internet connection.'})}\n\n"
        yield "data: [DONE]\n\n"
    except requests.exceptions.Timeout:
        yield f"data: {json.dumps({'error': 'The AI service timed out. Please try again.'})}\n\n"
        yield "data: [DONE]\n\n"
    except requests.exceptions.HTTPError as exc:
        yield f"data: {json.dumps({'error': f'AI service error: {exc.response.status_code}'})}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as exc:
        yield f"data: {json.dumps({'error': f'Unexpected error: {str(exc)}'})}\n\n"
        yield "data: [DONE]\n\n"


# ── Views ─────────────────────────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    POST /api/chatbot/chat/
    Body: { "message": str, "history": [{"role": str, "content": str}, ...] }
    Returns: text/event-stream SSE
    """
    message = request.data.get("message", "").strip()
    history = request.data.get("history", [])

    if not message:
        return Response(
            {"error": "message is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    system_prompt = _build_system_prompt(request.user)
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    response = StreamingHttpResponse(
        _agentic_stream(messages, request.user),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def analyse_file(request):
    """
    POST /api/chatbot/analyse-file/
    Accepts a multipart upload with a file (image or text-based document).
    Returns extracted key points as a suggested note.

    Supports: images (jpg, png, gif, webp) via vision API
              text files (txt, md) via direct content extraction
    """
    import base64
    import mimetypes

    uploaded = request.FILES.get("file")
    instruction = request.data.get("instruction", "Extract the key points from this file and format them as a concise note.")

    if not uploaded:
        return Response({"error": "file is required"}, status=status.HTTP_400_BAD_REQUEST)

    max_size = 10 * 1024 * 1024  # 10 MB
    if uploaded.size > max_size:
        return Response({"error": "File too large (max 10 MB)"}, status=status.HTTP_400_BAD_REQUEST)

    mime_type, _ = mimetypes.guess_type(uploaded.name)
    mime_type = mime_type or "application/octet-stream"
    is_image = mime_type.startswith("image/")
    is_text = mime_type in ("text/plain", "text/markdown") or uploaded.name.endswith((".txt", ".md"))

    if not is_image and not is_text:
        return Response(
            {"error": f"Unsupported file type '{mime_type}'. Supported: images (jpg/png/gif/webp) and text files (txt/md)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        if is_image:
            raw_bytes = uploaded.read()
            b64 = base64.b64encode(raw_bytes).decode("utf-8")
            data_url = f"data:{mime_type};base64,{b64}"
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": instruction},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ]
            model = "openai/gpt-4o-mini"
        else:
            # Plain text file
            content = uploaded.read().decode("utf-8", errors="replace")[:8000]
            messages = [
                {"role": "system", "content": "You extract key points from documents and format them as concise notes."},
                {"role": "user", "content": f"{instruction}\n\nDocument content:\n{content}"},
            ]
            model = MODEL

        resp = requests.post(
            OPENROUTER_CHAT_URL,
            json={"model": model, "messages": messages},
            headers=headers,
            timeout=60,
        )
        resp.raise_for_status()
        extracted = resp.json()["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as exc:
        return Response(
            {"error": f"AI service error: {str(exc)}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    # Suggest a title from the filename
    suggested_title = uploaded.name.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()

    return Response(
        {
            "payload": {
                "suggested_title": suggested_title,
                "extracted_content": extracted,
                "filename": uploaded.name,
            }
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def suggestions(request):
    """
    GET /api/chatbot/suggestions/
    Returns 3 smarter proactive suggestions based on pattern analysis of notes:
    - Stale notes that haven't been updated in a while
    - Notes with incomplete/todo language
    - Recurring topics across multiple notes
    """
    from django.utils import timezone

    all_notes = Note.objects.filter(
        created_by=request.user, is_trashed=False
    ).order_by("-updated_at")[:30]

    if not all_notes:
        return Response(
            {"payload": {"suggestions": [
                "Create your first note to get started",
                "Try asking me to organise your notes by topic",
                "You can set reminders on notes — just ask me",
            ]}},
            status=status.HTTP_200_OK,
        )

    now = timezone.now()
    notes_text_parts = []
    stale_count = 0
    todo_count = 0

    for n in all_notes:
        age_days = (now - n.updated_at).days
        if age_days > 7:
            stale_count += 1
        content_lower = (n.content or "").lower()
        if any(kw in content_lower for kw in ["todo", "to-do", "[ ]", "- [ ]", "need to", "must", "should"]):
            todo_count += 1
        notes_text_parts.append(
            f"- [id={n.pk}, age={age_days}d] {n.title or 'Untitled'}: {(n.content or '')[:150]}"
        )

    notes_text = "\n".join(notes_text_parts)

    context_hints = []
    if stale_count > 3:
        context_hints.append(f"{stale_count} notes haven't been updated in over a week")
    if todo_count > 0:
        context_hints.append(f"{todo_count} notes contain todo/task language")
    if len(all_notes) > 10:
        context_hints.append("the user has many notes that could benefit from organisation")

    hints_text = (" Context: " + "; ".join(context_hints) + ".") if context_hints else ""

    prompt = (
        f"You are an AI assistant for a note-taking app.{hints_text} "
        "Based on the user's notes below, generate exactly 3 short, specific, actionable suggestions "
        "(one sentence each) to help them. Focus on: stale notes that need updating, incomplete tasks, "
        "or topics that could be synthesised or organised. "
        "Return them as a JSON array of strings.\n\n"
        f"Notes:\n{notes_text}"
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Always respond with a valid JSON array of 3 strings, no markdown."},
        {"role": "user", "content": prompt},
    ]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            OPENROUTER_CHAT_URL,
            json={"model": MODEL, "messages": messages, "response_format": {"type": "json_object"}},
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        reply = resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as exc:
        return Response(
            {"error": f"AI service error: {str(exc)}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    try:
        parsed = json.loads(reply)
        if isinstance(parsed, dict):
            suggestion_list = next(
                (v for v in parsed.values() if isinstance(v, list)), []
            )
        elif isinstance(parsed, list):
            suggestion_list = parsed
        else:
            raise ValueError
        if not suggestion_list:
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        suggestion_list = [
            line.strip("- \"").strip()
            for line in reply.splitlines()
            if line.strip()
        ][:3]

    return Response(
        {"payload": {"suggestions": suggestion_list[:3]}},
        status=status.HTTP_200_OK,
    )