from rest_framework import serializers
from labels.models import Label
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    """
    Input/output serializer for Note.

    Read fields:  title, content, is_archived, labels (flat list of label titles).
    Write fields: title, content, is_archived, label_ids (list of label PKs, write-only).

    Excluded from output:
        - id          — internal DB identifier, not relevant to the user
        - is_trashed  — internal soft-delete flag, not shown to the user
        - label_ids   — write-only input field
    """

    # Read: render labels as a flat list of title strings
    labels = serializers.SerializerMethodField()

    # Write: accept a list of label PKs to associate
    label_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Label.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Note
        fields = ["title", "content", "color", "is_archived", "labels", "label_ids"]

    def get_labels(self, obj) -> list[str]:
        """Return label titles as a plain list of strings."""
        return [label.title for label in obj.labels.all()]

