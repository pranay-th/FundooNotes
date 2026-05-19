from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.response import error_response, success_response
from .serializers import LabelSerializer
from .services import (
    create_label,
    delete_label,
    get_label_or_403,
    get_labels_for_user,
    update_label,
)


@extend_schema(
    methods=["GET"],
    operation_id="labels_list",
    responses={200: LabelSerializer(many=True)},
)
@extend_schema(
    methods=["POST"],
    operation_id="labels_create",
    request=LabelSerializer,
    responses={201: LabelSerializer},
)
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def labels_list_create(request):
    """
    GET  /api/labels/  — list all labels owned by the authenticated user
    POST /api/labels/  — create a new label
    """
    if request.method == "GET":
        labels = get_labels_for_user(request.user)
        # Single-field output: return a flat list of title strings
        return Response(
            success_response(
                "Labels retrieved successfully.",
                [label.title for label in labels],
            ),
            status=status.HTTP_200_OK,
        )

    # POST
    serializer = LabelSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            error_response("Validation error.", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )
    label = create_label(request.user, serializer.validated_data)
    return Response(
        success_response("Label created successfully.", label.title),
        status=status.HTTP_201_CREATED,
    )


@extend_schema(
    methods=["GET"],
    operation_id="labels_retrieve",
    responses={200: LabelSerializer},
)
@extend_schema(
    methods=["PUT"],
    operation_id="labels_update",
    request=LabelSerializer,
    responses={200: LabelSerializer},
)
@extend_schema(
    methods=["PATCH"],
    operation_id="labels_partial_update",
    request=LabelSerializer,
    responses={200: LabelSerializer},
)
@extend_schema(
    methods=["DELETE"],
    operation_id="labels_destroy",
    responses={204: None},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def label_detail(request, pk: int):
    """
    GET    /api/labels/<pk>/  — retrieve a label
    PUT    /api/labels/<pk>/  — full update
    PATCH  /api/labels/<pk>/  — partial update
    DELETE /api/labels/<pk>/  — hard-delete
    """
    label = get_label_or_403(pk, request.user)

    if request.method == "GET":
        return Response(
            success_response("Label retrieved successfully.", label.title),
            status=status.HTTP_200_OK,
        )

    if request.method == "DELETE":
        delete_label(label)
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PUT or PATCH
    partial = request.method == "PATCH"
    serializer = LabelSerializer(label, data=request.data, partial=partial)
    if not serializer.is_valid():
        return Response(
            error_response("Validation error.", serializer.errors),
            status=status.HTTP_400_BAD_REQUEST,
        )
    updated = update_label(label, serializer.validated_data, partial=partial)
    return Response(
        success_response("Label updated successfully.", updated.title),
        status=status.HTTP_200_OK,
    )
