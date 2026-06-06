# FundooNotes AI Chatbot — Technical Reference

## Overview

The FundooNotes AI assistant is a fully agentic chatbot embedded in the application as a floating action button (FAB). It uses GPT-4o mini through OpenRouter and can perform real database operations — creating, editing, deleting notes and labels — not just describe what it would do.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Browser (React / Vite)                       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     ChatbotFAB.jsx                           │   │
│  │                                                              │   │
│  │  ┌─────────────┐   ┌──────────────┐   ┌─────────────────┐   │   │
│  │  │ SessionStore│   │ MessageList  │   │  Input / Mic /  │   │   │
│  │  │  (history,  │   │  (streaming  │   │  Attach Button  │   │   │
│  │  │  display)   │   │   bubbles)   │   │                 │   │   │
│  │  └─────────────┘   └──────────────┘   └─────────────────┘   │   │
│  │                                                              │   │
│  │  sendChatMessage()   ──── raw fetch + SSE reader ────────►  │   │
│  │  analyseFile()       ──── axios multipart POST ──────────►  │   │
│  │  getChatSuggestions() ── axios GET ───────────────────────►  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTPS
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   Django Backend  (Render.com)                      │
│                                                                     │
│  POST /api/chatbot/chat/         → views.chat()                     │
│  GET  /api/chatbot/suggestions/  → views.suggestions()              │
│  POST /api/chatbot/analyse-file/ → views.analyse_file()             │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    views.chat()                              │   │
│  │                                                              │   │
│  │  1. _build_system_prompt(user)                               │   │
│  │     ├── Query last 20 own notes (NeonDB)                     │   │
│  │     └── Query shared notes via note_collaborators (NeonDB)   │   │
│  │                                                              │   │
│  │  2. _run_agentic_loop(messages, user)  ◄──────────────────┐  │   │
│  │     ├── POST to OpenRouter (non-streaming, tools=[TOOLS])  │  │   │
│  │     ├── If tool_calls in response:                         │  │   │
│  │     │   └── executor.execute_tool(name, args, user) ───►   │  │   │
│  │     │       ├── list_notes / create_note / update_note     │  │   │
│  │     │       ├── delete_note / set_reminder                 │  │   │
│  │     │       ├── synthesize_notes (calls OpenRouter again)  │  │   │
│  │     │       ├── organise_notes_by_topic (calls OpenRouter) │  │   │
│  │     │       ├── list_labels / create_label / update_label  │  │   │
│  │     │       ├── delete_label                               │  │   │
│  │     │       └── list_shared_notes (raw SQL join)           │  │   │
│  │     │   └── Append tool result → loop back ────────────────┘  │   │
│  │     └── If no tool_calls: final text reply → break            │   │
│  │                                                              │   │
│  │  3. _stream_text(final_text)                                 │   │
│  │     └── Yield SSE: data: "word " \n\n  ... data: [DONE]\n\n  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                views.analyse_file()                          │   │
│  │  ├── Read uploaded file (image or .txt/.md)                  │   │
│  │  ├── Images → base64 encode → vision API (gpt-4o-mini)       │   │
│  │  └── Text → direct content → standard chat API              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                views.suggestions()                           │   │
│  │  ├── Query last 30 notes                                     │   │
│  │  ├── Analyse: stale (>7d), todo keywords, volume             │   │
│  │  └── Ask GPT for 3 specific actionable suggestions           │   │
│  └──────────────────────────────────────────────────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
    ┌──────────────┐   ┌──────────────────┐  ┌───────────────┐
    │  NeonDB       │   │  OpenRouter API  │  │  Render Redis │
    │  (PostgreSQL) │   │  (gpt-4o-mini)   │  │  (OTP cache,  │
    │               │   │                  │  │   note cache) │
    │  - notes      │   │  Tool calls:     │  └───────────────┘
    │  - labels     │   │  non-streaming   │
    │  - users      │   │                  │
    │  - note_      │   │  Final reply:    │
    │    collabora- │   │  streaming SSE   │
    │    tors       │   └──────────────────┘
    └──────────────┘
```

---

## Request Flow — Chat Message

```
User types message and hits Send
           │
           ▼
ChatbotFAB._send(text, fromVoice)
  │  Optimistically adds user bubble to displayMessages
  │  Sets loading=true, clears streamingContent
  │
  ▼
chatbotApi.sendChatMessage(message, history, onToken)
  │  Uses raw fetch() — axios doesn't support streaming
  │  Sends: { message, history: [{role, content}...] }
  │  Authorization: Bearer <JWT from localStorage>
  │
  ▼
Django: POST /api/chatbot/chat/
  │
  ├─ _build_system_prompt(user)
  │    Injects up to 20 own notes + up to 10 shared notes
  │    Each note: - [id=N] [Title]: content[:300]
  │    Reminders shown: [reminder: 2026-06-10T09:00:00+00:00]
  │
  ├─ _run_agentic_loop(messages, user)   [up to 10 iterations]
  │    │
  │    ├─ POST OpenRouter (non-streaming, tool_choice=auto)
  │    │    Model: openai/gpt-4o-mini
  │    │    Tools: 11 function definitions
  │    │
  │    ├─ If assistant.tool_calls:
  │    │    For each tool call:
  │    │      executor._dispatch(name, args, user)
  │    │        → DB write / read
  │    │        → Cache invalidation
  │    │      Append {role: tool, tool_call_id, content: JSON result}
  │    │    Loop back ──────────────────────────────────────────────┐
  │    │                                                            │
  │    └─ If no tool_calls: final text → break                     │
  │                                          ◄───────────────────── ┘
  │
  └─ StreamingHttpResponse(_stream_text(final_text))
       Splits reply by spaces → yields SSE chunks
       data: "word "\n\n ... data: [DONE]\n\n
       Headers: Content-Type: text/event-stream
                Cache-Control: no-cache
                X-Accel-Buffering: no

           │  SSE stream over HTTPS
           ▼
chatbotApi.sendChatMessage() — ReadableStream reader loop
  │  Parses SSE lines split by \n\n
  │  Calls onToken(token) for each word
  │
  ▼
ChatbotFAB
  │  onToken: setStreamingContent(prev => prev + token)
  │  → Live text renders in the loading bubble with blinking cursor
  │
  ▼
Stream ends ([DONE] received)
  │  fullReply assembled from all tokens
  │  updatedHistory = [...history, {user}, {assistant}]
  │  setHistory(updatedHistory)   → persisted to sessionStorage
  │  setDisplayMessages(toDisplayMessages(updatedHistory))
  │  setStreamingContent('')      → streaming bubble replaced by final bubble
  │  React Query invalidations: ['notes'], ['labels'], ['shared-notes']
```

---

## Request Flow — File Upload

```
User clicks 📎 and selects a file
           │
           ▼
handleFileChange(event)
  │  Reads file from input, clears the input ref
  │  Sets fileUploading=true, pendingFile={name}
  │
  ▼
chatbotApi.analyseFile(file)
  │  POST /api/chatbot/analyse-file/  (multipart/form-data)
  │  Field: file=<binary>
  │
  ▼
Django: views.analyse_file()
  │
  ├─ Validate: max 10 MB, mime type must be image/* or text/plain or text/md
  │
  ├─ Images (jpg/png/gif/webp):
  │    base64 encode → OpenRouter vision API
  │    Model: openai/gpt-4o-mini
  │    Message: [{role: user, content: [{type: text}, {type: image_url}]}]
  │
  └─ Text files (.txt/.md):
       Read up to 8000 chars → standard chat API
       Model: openai/gpt-4o-mini
  │
  └─ Returns: { suggested_title, extracted_content, filename }

           │
           ▼
handleFileChange() — success path
  │  Creates assistant preview message:
  │    "I've analysed <filename>. Here's what I extracted:
  │     <extracted_content>
  │     What would you like to do with this?"
  │
  ├─ setDisplayMessages([...prev, assistantPreview])
  └─ setHistory([...prev, {role:user, file context}, {role:assistant, preview}])

User now types follow-up: "create a note with just the skills section"
  → Normal _send() flow with file context already in history
```

---

## Request Flow — Suggestions

```
ChatbotFAB opens (first time, no prior messages)
           │
           ▼
fetchSuggestions()
  │  GET /api/chatbot/suggestions/
  │
  ▼
Django: views.suggestions()
  │
  ├─ Query last 30 non-trashed notes
  │
  ├─ Pattern analysis:
  │    stale_count:  notes not updated in >7 days
  │    todo_count:   notes containing "todo", "[ ]", "need to", "must", "should"
  │    volume check: >10 notes → suggest organisation
  │
  ├─ Build context hint string:
  │    "Context: 5 notes haven't been updated in over a week;
  │     3 notes contain todo/task language."
  │
  └─ POST OpenRouter (response_format: json_object)
       Prompt: "Generate 3 specific actionable suggestions..."
       Returns: ["suggestion 1", "suggestion 2", "suggestion 3"]

           │
           ▼
Rendered as clickable Chip components
  onClick → _send(suggestion) — fires the suggestion as a message
```

---

## Available Tools

| Tool | Description | DB Operation |
|---|---|---|
| `list_notes` | List all non-trashed own notes | SELECT notes |
| `create_note` | Create a note | INSERT note + cache invalidate |
| `update_note` | Update title/content/color/archived/trashed | UPDATE note + cache invalidate |
| `delete_note` | Soft-delete (is_trashed=True) | UPDATE note.is_trashed + cache invalidate |
| `set_reminder` | Set or clear reminder_at datetime | UPDATE note.reminder_at |
| `synthesize_notes` | Create new note combining N notes | OpenRouter call + INSERT note |
| `organise_notes_by_topic` | Auto-label all notes by topic | OpenRouter call + INSERT labels + UPDATE note_labels |
| `list_labels` | List all labels | SELECT labels |
| `create_label` | Create a label | INSERT label |
| `update_label` | Rename a label | UPDATE label |
| `delete_label` | Delete a label | DELETE label |
| `list_shared_notes` | List notes shared with user by others | Raw SQL JOIN note_collaborators + notes |

---

## Session Persistence

Chat state persists in `sessionStorage` so history survives page refreshes within the same tab but clears on logout or new tab.

| Key | Contents |
|---|---|
| `fundoo_chat_history` | Full `[{role, content}]` array sent to the API |
| `fundoo_chat_display` | Display messages `[{role, content, timestamp, fromVoice}]` |

Both are cleared on `handleClear()` and when `AuthContext.logout()` is called.

---

## Reminder System

Note reminders use a cron-job.org webhook instead of Celery Beat (free tier constraint).

```
cron-job.org (every 60s)
    │
    │  POST /api/cron/trigger-reminders/
    │  Header: X-Cron-Secret: <secret>
    │
    ▼
Django: common.cron_views.trigger_reminders()
    │  Validates HMAC secret header
    │
    ▼
common.tasks.dispatch_due_reminders()
    │  Query: notes WHERE reminder_at <= now() AND reminder_at >= now()-1min
    │         AND is_trashed=False
    │
    ├─ For each due note:
    │    send_mail() to note.created_by.email
    │    Set note.reminder_at = None  (single-fire)
    │
    └─ Return
```

---

## Key Files

```
fundoonotes/
├── chatbot/
│   ├── views.py       # chat(), suggestions(), analyse_file() endpoints
│   ├── executor.py    # Tool dispatch → ORM operations
│   ├── tools.py       # OpenAI-style tool schema definitions
│   └── urls.py        # Route registration
├── common/
│   ├── tasks.py       # dispatch_due_reminders() Celery task
│   └── cron_views.py  # trigger_reminders() HTTP endpoint for cron-job.org
└── notes/
    └── models.py      # Note model with reminder_at field

fundoonotes-frontend/src/
├── components/chatbot/
│   └── ChatbotFAB.jsx # Full chat UI: streaming, voice, file upload, suggestions
├── api/
│   └── chatbotApi.js  # sendChatMessage (SSE), getChatSuggestions, analyseFile
└── hooks/
    └── useSpeechRecognition.js  # Web Speech API wrapper
```

---

## Environment Variables

| Variable | Used by | Purpose |
|---|---|---|
| `CHATBOT_OPENROUTER_API_KEY` | Django | OpenRouter API key for GPT-4o mini |
| `CRON_SECRET` | Django | HMAC secret for cron endpoint authentication |
| `VITE_DJANGO_API_URL` | Frontend | Base URL for all Django API calls |
