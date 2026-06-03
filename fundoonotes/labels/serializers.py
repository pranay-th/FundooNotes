from rest_framework import serializers

from .models import Label


class LabelSerializer(serializers.ModelSerializer):
    """
    Input/output serializer for Label.

    Output fields: id, title, created_at, updated_at
    Input fields:  title (required, unique per user — enforced in service layer).
    """

    class Meta:
        model = Label
        fields = ["id", "title", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
