from rest_framework import serializers

from .models import Label


class LabelSerializer(serializers.ModelSerializer):
    """
    Serializer for the Label model.

    Preconditions:
        - title: non-empty string, max 100 chars
    Postconditions:
        - id, created_at, updated_at are read-only
        - created_by is excluded from input/output (set by service layer)
    """

    class Meta:
        model = Label
        fields = ["id", "title", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
