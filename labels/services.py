from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from .models import Label


def get_labels_for_user(user):
    """
    Returns all labels owned by the given user.

    Postconditions:
        - Every label in the returned queryset satisfies label.created_by == user
    """
    return Label.objects.filter(created_by=user)


def create_label(user, validated_data: dict) -> Label:
    """
    Creates a label owned by `user`.

    Preconditions:
        - validated_data contains a non-empty 'title'
    Postconditions:
        - Label created with created_by=user
        - Raises ValidationError on duplicate (title, user) combination
    """
    try:
        label = Label.objects.create(created_by=user, **validated_data)
    except IntegrityError:
        raise ValidationError(
            {"title": "A label with this title already exists for your account."}
        )
    return label


def get_label_or_403(label_id: int, user) -> Label:
    """
    Returns the label if it exists and belongs to `user`.

    Raises:
        Http404: if the label does not exist
        PermissionDenied: if the label is not owned by user
    """
    label = get_object_or_404(Label, pk=label_id)
    if label.created_by != user:
        raise PermissionDenied("You do not have permission to access this label.")
    return label


def update_label(label: Label, validated_data: dict, partial: bool = False) -> Label:
    """
    Updates label fields and saves.

    Preconditions:
        - label is owned by the requesting user (enforced before calling)
        - validated_data contains valid field values
    Postconditions:
        - label fields updated and persisted
        - Raises ValidationError on duplicate title for the same user
    """
    for field, value in validated_data.items():
        setattr(label, field, value)
    try:
        label.save()
    except IntegrityError:
        raise ValidationError(
            {"title": "A label with this title already exists for your account."}
        )
    return label


def delete_label(label: Label) -> None:
    """
    Hard-deletes the label record from the database.

    Postconditions:
        - Label no longer exists in the database
    """
    label.delete()
