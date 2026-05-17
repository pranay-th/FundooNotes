from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("labels", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Note",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("content", models.TextField(blank=True)),
                ("is_archived", models.BooleanField(default=False)),
                ("is_trashed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="notes",
                    to=settings.AUTH_USER_MODEL,
                )),
                ("labels", models.ManyToManyField(
                    blank=True,
                    related_name="notes",
                    to="labels.label",
                )),
            ],
            options={
                "db_table": "notes",
                "ordering": ["-created_at"],
            },
        ),
    ]
