from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.response import error_response, success_response
from .serializers import NoteSerializer
from .services import (
    create_note,
    delete_note,
    get_note_or_403,
    get_notes_for_user,
    update_note,
)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def notes_list_create(request):
    """
    GET  /api/notes/  — list non-trashed notes for the authenticated user
    POST /api/notes/  — create a new note
    """
    if request.method == "GET":
        notes = get_notes_for_user(request.user.id)
        serializer = NoteSerializer(notes, many=True)
        return Response(
            success_response("Notes retrieved successfully.", serializer.data),
            status=status.HTTP_200_OK,
        )

    # POST
    serializer = NoteSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            error_response("Validation error.", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )
    note = create_note(request.user, serializer.validated_data)
    out = NoteSerializer(note)
    return Response(
        success_response("Note created successfully.", out.data),
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def note_detail(request, pk: int):
    """
    GET    /api/notes/<pk>/  — retrieve a note
    PUT    /api/notes/<pk>/  — full update
    PATCH  /api/notes/<pk>/  — partial update
    DELETE /api/notes/<pk>/  — soft-delete
    """
    note = get_note_or_403(pk, request.user)

    if request.method == "GET":
        cache_key = f"note_detail_{pk}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(
                success_response("Note retrieved successfully.", cached),
                status=status.HTTP_200_OK,
            )
        serializer = NoteSerializer(note)
        cache.set(cache_key, serializer.data, timeout=300)
        return Response(
            success_response("Note retrieved successfully.", serializer.data),
            status=status.HTTP_200_OK,
        )

    if request.method == "DELETE":
        delete_note(note)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PUT or PATCH
    partial = request.method == "PATCH"
    serializer = NoteSerializer(note, data=request.data, partial=partial)
    if not serializer.is_valid():
        return Response(
            error_response("Validation error.", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )
    updated = update_note(note, serializer.validated_data, partial=partial)
    out = NoteSerializer(updated)
    return Response(
        success_response("Note updated successfully.", out.data),
        status=status.HTTP_200_OK,
    )
