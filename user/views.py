from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegistrationSerializer
from .permissions import IsOwnerOrReadOnly
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema_view,
)

User = get_user_model()


@extend_schema_view(
    list=extend_schema(
        tags=["users"],
        summary="List users",
        description="Retrieves a list of all users.",
        responses={
            200: UserSerializer(many=True),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    ),
    retrieve=extend_schema(
        tags=["users"],
        summary="Retrieve user",
        description="Retrieves details of a specific user.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="User ID"),
        ],
        responses={
            200: UserSerializer,
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="User not found"),
        },
    ),
    create=extend_schema(
        tags=["users"],
        summary="Create user",
        description="Creates a new user account.",
        request=UserRegistrationSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description="Invalid input data"),
        },
    ),
    update=extend_schema(
        tags=["users"],
        summary="Update user",
        description="Updates an existing user's information.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="User ID"),
        ],
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            403: OpenApiResponse(
                description="You do not have permission to perform this action."
            ),
            404: OpenApiResponse(description="User not found"),
        },
    ),
    destroy=extend_schema(
        tags=["users"],
        summary="Delete user",
        description="Deletes a user account.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="User ID"),
        ],
        responses={
            204: OpenApiResponse(description="User deleted successfully"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            403: OpenApiResponse(
                description="You do not have permission to perform this action."
            ),
            404: OpenApiResponse(description="User not found"),
        },
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts and profiles.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegistrationSerializer
        return UserSerializer

    @extend_schema(
        tags=["users"],
        summary="Get current user profile",
        description="Retrieves the profile of the currently authenticated user.",
        responses={
            200: UserSerializer,
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        tags=["users"],
        summary="Register new user",
        description="Creates a new user account with the provided credentials.",
        request=UserRegistrationSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description="Invalid input data."),
        },
    )
    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["users"],
        summary="Change user password",
        description="Changes the password for the specified user account.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="User ID"),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "old_password": {"type": "string"},
                    "new_password": {"type": "string"},
                },
                "required": ["old_password", "new_password"],
            }
        },
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(
                description="Invalid input data or old password"
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            403: OpenApiResponse(
                description="You do not have permission to perform this action."
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def change_password(self, request, pk=None):
        user = self.get_object()
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not old_password or not new_password:
            return Response(
                {"error": "Both old and new passwords are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(old_password):
            return Response(
                {"error": "Invalid old password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password changed successfully"})

    @extend_schema(
        tags=["users"],
        summary="Update user profile",
        description="Updates the profile information for the specified user.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="User ID"),
        ],
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            403: OpenApiResponse(
                description="You do not have permission to perform this action."
            ),
        },
    )
    @action(detail=True, methods=["post"])
    def update_profile(self, request, pk=None):
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
