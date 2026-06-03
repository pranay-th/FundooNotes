"""
seed_data.py — Populate the live fundooNotes backend with sample data.

Uses factory-boy to generate realistic labels and notes, then POSTs them
to the running API using the provided access token (user_id=5).

Usage:
    python seed_data.py
    python seed_data.py --base-url http://127.0.0.1:8000
    python seed_data.py --token <your_access_token>

Requirements:
    pip install requests factory-boy faker
"""

import argparse
import random
import sys

import factory
import requests
from faker import Faker

fake = Faker()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzc5MTAzNTI2LCJpYXQiOjE3NzkwOTk5MjYs"
    "Imp0aSI6IjRiZmI3YTU3Yjg0MzQxMWZiNjdiMjU0ZTE3YTAyOWZkIiwidXNlcl9pZCI6IjUifQ"
    ".dj4PQOZ-CTb7deIpyLhHEFtlZANAa48O2Qx00cfQe4w"
)

# ---------------------------------------------------------------------------
# Factory definitions (no DB — just generate plain dicts)
# ---------------------------------------------------------------------------

LABEL_TITLES = [
    "Work", "Personal", "Ideas", "Shopping", "Travel",
    "Health", "Finance", "Learning", "Urgent", "Someday",
]

NOTE_TEMPLATES = [
    {
        "title": "Meeting notes — Q3 planning",
        "content": (
            "Discussed roadmap priorities for Q3.\n"
            "Action items:\n"
            "- Finalize API design by Friday\n"
            "- Review infra costs with DevOps\n"
            "- Schedule follow-up for next Monday"
        ),
        "label_names": ["Work", "Urgent"],
    },
    {
        "title": "Book recommendations",
        "content": (
            "1. Designing Data-Intensive Applications — Kleppmann\n"
            "2. Clean Architecture — Robert C. Martin\n"
            "3. The Pragmatic Programmer — Hunt & Thomas\n"
            "4. Staff Engineer — Will Larson"
        ),
        "label_names": ["Learning", "Personal"],
    },
    {
        "title": "Grocery list",
        "content": (
            "- Milk\n- Eggs\n- Bread\n- Olive oil\n"
            "- Spinach\n- Chicken breast\n- Greek yogurt"
        ),
        "label_names": ["Shopping"],
    },
    {
        "title": "Trip to Goa — packing list",
        "content": (
            "Clothes: 3 t-shirts, 2 shorts, swimwear\n"
            "Documents: ID, hotel booking, flight tickets\n"
            "Gadgets: charger, earphones, power bank\n"
            "Misc: sunscreen, sunglasses, flip-flops"
        ),
        "label_names": ["Travel", "Personal"],
    },
    {
        "title": "Startup idea — AI recipe generator",
        "content": (
            "Core concept: user inputs available ingredients, "
            "AI suggests recipes with step-by-step instructions.\n"
            "Monetisation: freemium + premium meal-plan subscriptions.\n"
            "Tech stack: FastAPI backend, React frontend, OpenAI API."
        ),
        "label_names": ["Ideas"],
    },
    {
        "title": "Monthly budget — May 2026",
        "content": (
            "Income:  ₹85,000\n"
            "Rent:    ₹18,000\n"
            "Food:    ₹8,000\n"
            "Travel:  ₹3,500\n"
            "Savings: ₹20,000\n"
            "Misc:    ₹5,000"
        ),
        "label_names": ["Finance"],
    },
    {
        "title": "Workout plan — this week",
        "content": (
            "Mon: chest + triceps\n"
            "Tue: back + biceps\n"
            "Wed: rest / walk\n"
            "Thu: legs\n"
            "Fri: shoulders + core\n"
            "Sat: cardio 30 min\n"
            "Sun: rest"
        ),
        "label_names": ["Health"],
    },
    {
        "title": "Django REST Framework — study notes",
        "content": (
            "Key concepts:\n"
            "- Serializers: validation + representation\n"
            "- ViewSets vs FBVs — project uses FBVs with @api_view\n"
            "- JWT auth via simplejwt\n"
            "- Throttling: AnonRateThrottle + UserRateThrottle\n"
            "- drf-spectacular for OpenAPI docs"
        ),
        "label_names": ["Learning", "Work"],
    },
    {
        "title": "Random thoughts",
        "content": fake.paragraph(nb_sentences=5),
        "label_names": ["Personal", "Someday"],
    },
    {
        "title": "Archived — old project tasks",
        "content": (
            "Legacy tasks from the previous sprint.\n"
            "Kept for reference only — no action needed."
        ),
        "label_names": ["Work"],
        "is_archived": True,
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def post(base_url: str, path: str, token: str, payload: dict) -> requests.Response:
    return requests.post(
        f"{base_url.rstrip('/')}{path}",
        json=payload,
        headers=headers(token),
        timeout=10,
    )


def ok(resp: requests.Response, label: str) -> bool:
    if resp.status_code in (200, 201):
        return True
    print(f"  ✗  {label} — HTTP {resp.status_code}: {resp.text[:200]}")
    return False


# ---------------------------------------------------------------------------
# Seed logic
# ---------------------------------------------------------------------------

def seed(base_url: str, token: str) -> None:
    print(f"\n🌱  Seeding fundooNotes at {base_url}\n")

    # ── 1. Create labels ────────────────────────────────────────────────────
    print("── Labels ──────────────────────────────────────────────────────")
    label_id_map: dict[str, int] = {}   # title → id

    for title in LABEL_TITLES:
        resp = post(base_url, "/api/labels/", token, {"title": title})
        if ok(resp, f"label '{title}'"):
            label_id = resp.json()["payload"]["id"]
            label_id_map[title] = label_id
            print(f"  ✓  Label created  id={label_id}  title='{title}'")
        else:
            # Might already exist — try to find it from a list call
            pass

    # ── 2. Fetch existing labels to fill any gaps (idempotent re-runs) ──────
    list_resp = requests.get(
        f"{base_url.rstrip('/')}/api/labels/",
        headers=headers(token),
        timeout=10,
    )
    if list_resp.ok:
        for lbl in list_resp.json().get("payload", []):
            label_id_map.setdefault(lbl["title"], lbl["id"])

    print(f"\n  Label map: {label_id_map}\n")

    # ── 3. Create notes ─────────────────────────────────────────────────────
    print("── Notes ───────────────────────────────────────────────────────")
    for tmpl in NOTE_TEMPLATES:
        # Resolve label names → IDs (skip any label not in map)
        ids = [label_id_map[n] for n in tmpl.get("label_names", []) if n in label_id_map]

        payload: dict = {
            "title":   tmpl["title"],
            "content": tmpl["content"],
        }
        if ids:
            payload["label_ids"] = ids
        if tmpl.get("is_archived"):
            payload["is_archived"] = True

        resp = post(base_url, "/api/notes/", token, payload)
        if ok(resp, f"note '{tmpl['title']}'"):
            note_id = resp.json()["payload"]["id"]
            tag_str = ", ".join(tmpl.get("label_names", [])) or "—"
            archived = " [archived]" if tmpl.get("is_archived") else ""
            print(f"  ✓  Note created   id={note_id}  '{tmpl['title']}'{archived}  labels=[{tag_str}]")

    # ── 4. Summary ──────────────────────────────────────────────────────────
    print("\n── Summary ─────────────────────────────────────────────────────")
    notes_resp  = requests.get(f"{base_url.rstrip('/')}/api/notes/",  headers=headers(token), timeout=10)
    labels_resp = requests.get(f"{base_url.rstrip('/')}/api/labels/", headers=headers(token), timeout=10)

    n_notes  = len(notes_resp.json().get("payload", []))  if notes_resp.ok  else "?"
    n_labels = len(labels_resp.json().get("payload", [])) if labels_resp.ok else "?"

    print(f"  Total notes  visible to user: {n_notes}")
    print(f"  Total labels visible to user: {n_labels}")
    print("\n✅  Seeding complete.\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed fundooNotes with sample data.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Backend base URL")
    parser.add_argument("--token",    default=DEFAULT_TOKEN,    help="JWT access token")
    args = parser.parse_args()

    try:
        seed(args.base_url, args.token)
    except requests.exceptions.ConnectionError:
        print(f"\n❌  Could not connect to {args.base_url}. Is the Django server running?\n")
        sys.exit(1)
