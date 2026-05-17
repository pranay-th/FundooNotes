from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import RegisterSerializer

# Create your views here.
@api_view(['POST'])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        return Response(
            {
                "message":"User created succesfully",
                "payload":serializer.data,
                "status":201
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(
        {
            "message":"Validation failed",
            "payload":serializer.errors,
            "status":400
        },
        status=status.HTTP_400_BAD_REQUEST
    )