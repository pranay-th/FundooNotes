from rest_framework import serializers
from labels.models import Label
from labels.serializers import LabelSerializer
from .models import Note


class NoteSerializer(serializers.ModelSerializer):
    """
    Input/output serializer for Note.

    Read fields:  id, title, content, color, is_archived, is_trashed,
                  labels (list of {id, title, created_at, updated_at}),
                  created_at, updated_at.
    Write fields: title, content, color, is_archived, is_trashed,
                  label_ids (list of label PKs, write-only).
    """

    # Read: render labels as full objects
    labels = LabelSerializer(many=True, read_only=True)

    # Write: accept a list of label PKs to associate
    label_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Label.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Note
        fields = [
            "id", "title", "content", "color",
            "is_archived", "is_trashed",
            "labels", "label_ids",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
