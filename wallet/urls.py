from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WalletViewSet

router = DefaultRouter()
router.register(r"wallets", WalletViewSet, basename="wallet")

urlpatterns = [
    path("", include(router.urls)),
]
