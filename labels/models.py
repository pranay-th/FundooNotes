from django.db import models
from django.conf import settings


class Label(models.Model):
    title      = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="labels",
    )

    class Meta:
        db_table = "labels"
        unique_together = ("title", "created_by")

    def __str__(self):
        return self.title
