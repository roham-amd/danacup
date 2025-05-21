from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet,
    WalletDetailView,
    WalletDepositView,
    WalletWithdrawView,
    TransactionListView,
)

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("", include(router.urls)),
    # Wallet endpoints
    path("wallet/", WalletDetailView.as_view(), name="wallet-detail"),
    path(
        "wallet/deposit/",
        WalletDepositView.as_view(),
        name="wallet-deposit",
    ),
    path(
        "wallet/withdraw/",
        WalletWithdrawView.as_view(),
        name="wallet-withdraw",
    ),
    # Transaction endpoints
    path(
        "transactions/",
        TransactionListView.as_view(),
        name="transaction-list",
    ),
]
