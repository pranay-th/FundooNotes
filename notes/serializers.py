from rest_framework import serializers
from labels.models import Label
from .models import Note


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ["id", "title"]


class NoteSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Label.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Note
        fields = [
            "id", "title", "content", "is_archived", "is_trashed",
            "labels", "label_ids", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
