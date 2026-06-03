from django.db import models
from django.conf import settings


class Note(models.Model):
    COLOR_CHOICES = [
        ("default", "Default"),
        ("red",     "Red"),
        ("orange",  "Orange"),
        ("yellow",  "Yellow"),
        ("green",   "Green"),
        ("teal",    "Teal"),
        ("blue",    "Blue"),
        ("purple",  "Purple"),
        ("pink",    "Pink"),
        ("brown",   "Brown"),
        ("gray",    "Gray"),
    ]

    title       = models.CharField(max_length=255)
    content     = models.TextField(blank=True)
    color       = models.CharField(max_length=20, choices=COLOR_CHOICES, default="default")
    is_archived = models.BooleanField(default=False)
    is_trashed  = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    created_by  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    labels = models.ManyToManyField(
        "labels.Label",
        blank=True,
        related_name="notes",
    )

    class Meta:
        db_table = "notes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
