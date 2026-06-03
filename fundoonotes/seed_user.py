"""
Seed notes and labels for the current user directly via Django ORM.
Run with: python manage.py shell < seed_user.py
Or:       python manage.py runscript seed_user (with django-extensions)
"""
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fundoonotes.settings')
django.setup()

from users.models import User
from notes.models import Note
from labels.models import Label

USERNAME = 'pranayth'

try:
    u = User.objects.get(username=USERNAME)
except User.DoesNotExist:
    print(f"User '{USERNAME}' not found. Run this after registering.")
    exit(1)

print(f"Seeding data for user: {u.username} ({u.email})\n")

# ── Labels ────────────────────────────────────────────────────────────────────
label_titles = [
    'Work', 'Personal', 'Ideas', 'Shopping', 'Travel',
    'Health', 'Finance', 'Learning', 'Urgent', 'Someday',
]
label_map = {}
for title in label_titles:
    lbl, created = Label.objects.get_or_create(created_by=u, title=title)
    label_map[title] = lbl
    status = 'created' if created else 'exists'
    print(f"  Label [{status}]: {title} (id={lbl.id})")

print()

# ── Notes ─────────────────────────────────────────────────────────────────────
templates = [
    {
        'title': 'Meeting notes — Q3 planning',
        'content': (
            'Discussed roadmap priorities for Q3.\n'
            'Action items:\n'
            '- Finalize API design by Friday\n'
            '- Review infra costs with DevOps\n'
            '- Schedule follow-up for next Monday'
        ),
        'labels': ['Work', 'Urgent'],
        'color': 'yellow',
    },
    {
        'title': 'Book recommendations',
        'content': (
            '1. Designing Data-Intensive Applications — Kleppmann\n'
            '2. Clean Architecture — Robert C. Martin\n'
            '3. The Pragmatic Programmer — Hunt & Thomas\n'
            '4. Staff Engineer — Will Larson'
        ),
        'labels': ['Learning', 'Personal'],
        'color': 'blue',
    },
    {
        'title': 'Grocery list',
        'content': (
            '- Milk\n- Eggs\n- Bread\n- Olive oil\n'
            '- Spinach\n- Chicken breast\n- Greek yogurt'
        ),
        'labels': ['Shopping'],
        'color': 'green',
    },
    {
        'title': 'Trip to Goa — packing list',
        'content': (
            'Clothes: 3 t-shirts, 2 shorts, swimwear\n'
            'Documents: ID, hotel booking, flight tickets\n'
            'Gadgets: charger, earphones, power bank\n'
            'Misc: sunscreen, sunglasses, flip-flops'
        ),
        'labels': ['Travel', 'Personal'],
        'color': 'teal',
    },
    {
        'title': 'Startup idea — AI recipe generator',
        'content': (
            'Core concept: user inputs available ingredients, '
            'AI suggests recipes with step-by-step instructions.\n'
            'Monetisation: freemium + premium meal-plan subscriptions.\n'
            'Tech stack: FastAPI backend, React frontend, OpenAI API.'
        ),
        'labels': ['Ideas'],
        'color': 'purple',
    },
    {
        'title': 'Monthly budget — May 2026',
        'content': (
            'Income:  85,000\n'
            'Rent:    18,000\n'
            'Food:     8,000\n'
            'Travel:   3,500\n'
            'Savings: 20,000\n'
            'Misc:     5,000'
        ),
        'labels': ['Finance'],
        'color': 'orange',
    },
    {
        'title': 'Workout plan — this week',
        'content': (
            'Mon: chest + triceps\n'
            'Tue: back + biceps\n'
            'Wed: rest / walk\n'
            'Thu: legs\n'
            'Fri: shoulders + core\n'
            'Sat: cardio 30 min\n'
            'Sun: rest'
        ),
        'labels': ['Health'],
        'color': 'red',
    },
    {
        'title': 'Django REST Framework — study notes',
        'content': (
            'Key concepts:\n'
            '- Serializers: validation + representation\n'
            '- ViewSets vs FBVs — project uses FBVs with @api_view\n'
            '- JWT auth via simplejwt\n'
            '- Throttling: AnonRateThrottle + UserRateThrottle\n'
            '- drf-spectacular for OpenAPI docs'
        ),
        'labels': ['Learning', 'Work'],
        'color': 'default',
    },
    {
        'title': 'Random thoughts',
        'content': (
            'Sometimes the best ideas come when you least expect them.\n'
            'Keep a note of everything — you never know what will be useful.\n'
            'The key is to review your notes regularly.'
        ),
        'labels': ['Personal', 'Someday'],
        'color': 'pink',
    },
    {
        'title': 'Archived — old project tasks',
        'content': (
            'Legacy tasks from the previous sprint.\n'
            'Kept for reference only — no action needed.'
        ),
        'labels': ['Work'],
        'color': 'gray',
        'is_archived': True,
    },
]

created_count = 0
for t in templates:
    # Skip if note with same title already exists for this user
    if Note.objects.filter(created_by=u, title=t['title']).exists():
        print(f"  Note [exists]:  {t['title']}")
        continue

    note = Note.objects.create(
        created_by=u,
        title=t['title'],
        content=t['content'],
        color=t.get('color', 'default'),
        is_archived=t.get('is_archived', False),
    )
    for lname in t.get('labels', []):
        if lname in label_map:
            note.labels.add(label_map[lname])

    archived_tag = ' [archived]' if t.get('is_archived') else ''
    labels_tag = ', '.join(t.get('labels', []))
    print(f"  Note [created]: {t['title']}{archived_tag}  labels=[{labels_tag}]")
    created_count += 1

print(f"\nDone! Created {created_count} notes and {len(label_titles)} labels (skipped existing).")
