
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .serializers import UserSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom token serializer that also returns user data
    """

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user details to the response
        user = self.user
        data["user"] = UserSerializer(user).data

        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Takes a set of user credentials and returns access and refresh tokens
    along with user data. The API is designed to work with either username,
    email, or phone_number as the identifier.
    """

    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        operation_id="token_obtain_pair",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="JWT token pair obtained successfully",
                response={
                    "type": "object",
                    "properties": {
                        "refresh": {"type": "string"},
                        "access": {"type": "string"},
                        "user": {"type": "object"},
                    },
                },
            )
        },
        description="Obtain JWT token pair with "
        "username/email/phone + password",
        summary="Obtain JWT Token",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    """
    Takes a refresh token and returns a new access token
    """

    @extend_schema(
        operation_id="token_refresh",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Access token refreshed successfully",
                response={
                    "type": "object",
                    "properties": {
                        "access": {"type": "string"},
                    },
                },
            )
        },
        description="Refresh access token using refresh token",
        summary="Refresh Access Token",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenVerifyView(TokenVerifyView):
    """
    Takes a token and indicates if it is valid
    """

    @extend_schema(
        operation_id="token_verify",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="Token is valid",
                response={
                    "type": "object",
                    "properties": {},
                },
            )
        },
        description="Verify if a token is valid",
        summary="Verify Token",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

