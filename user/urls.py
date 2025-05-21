from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet
from .jwt_views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
)


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")


urlpatterns = [
    path("", include(router.urls)),
    # JWT Token endpoints
    path(
        "token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path(
        "token/refresh/",
        CustomTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "token/verify/", CustomTokenVerifyView.as_view(), name="token_verify"
    ),
]
