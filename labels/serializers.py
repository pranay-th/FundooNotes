from rest_framework import serializers

from .models import Label


class LabelSerializer(serializers.ModelSerializer):
    """
    Input/output serializer for Label.

    Output fields: title only — id and timestamps are internal.
    Input fields:  title (required, unique per user — enforced in service layer).
    """

    class Meta:
        model = Label
        fields = ["title"]
        
