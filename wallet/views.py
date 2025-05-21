from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

# Create your views here.


class WalletViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user wallets.
    Provides endpoints for wallet operations like deposits, withdrawals,
    transaction history, and balance checking.
    """

    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=["wallet"],
        summary="List wallets",
        description="Retrieves a list of all wallets for the authenticated user.",
        responses={
            200: WalletSerializer(many=True),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["wallet"],
        summary="Retrieve wallet",
        description="Retrieves details of a specific wallet.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Wallet ID"),
        ],
        responses={
            200: WalletSerializer,
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Wallet not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["wallet"],
        summary="Create wallet",
        description="Creates a new wallet for the authenticated user.",
        request=WalletSerializer,
        responses={
            201: WalletSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["wallet"],
        summary="Update wallet",
        description="Updates an existing wallet.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Wallet ID"),
        ],
        request=WalletSerializer,
        responses={
            200: WalletSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Wallet not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["wallet"],
        summary="Delete wallet",
        description="Deletes a wallet.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Wallet ID"),
        ],
        responses={
            204: OpenApiResponse(description="Wallet deleted successfully"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Wallet not found"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["wallet"],
        summary="Deposit funds",
        description="Adds funds to the wallet balance.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Wallet ID"),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "minimum": 0.01},
                },
                "required": ["amount"],
            }
        },
        responses={
            200: TransactionSerializer,
            400: OpenApiResponse(description="Invalid amount provided"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Wallet not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def deposit(self, request, pk=None):
        wallet = self.get_object()
        amount = request.data.get("amount")

        if not amount or float(amount) <= 0:
            return Response(
                {"error": "Valid amount is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            transaction = wallet.deposit(float(amount))
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["wallet"],
        summary="Withdraw funds",
        description="Withdraws funds from the wallet balance.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Wallet ID"),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "minimum": 0.01},
                },
                "required": ["amount"],
            }
        },
        responses={
            200: TransactionSerializer,
            400: OpenApiResponse(
                description="Invalid amount or insufficient funds"
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Wallet not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def withdraw(self, request, pk=None):
        wallet = self.get_object()
        amount = request.data.get("amount")

        if not amount or float(amount) <= 0:
            return Response(
                {"error": "Valid amount is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            transaction = wallet.withdraw(float(amount))
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["wallet"],
        summary="Get transaction history",
        description="Retrieves the transaction history for the wallet.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Wallet ID"),
        ],
        responses={
            200: TransactionSerializer(many=True),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Wallet not found"),
        },
    )
    @action(detail=True, methods=["get"])
    def transactions(self, request, pk=None):
        wallet = self.get_object()
        transactions = Transaction.objects.filter(wallet=wallet).order_by(
            "-created_at"
        )
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    @extend_schema(
        tags=["wallet"],
        summary="Get wallet balance",
        description="Retrieves the current balance of the wallet.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Wallet ID"),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "balance": {"type": "number"},
                    "currency": {"type": "string"},
                },
            },
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Wallet not found"),
        },
    )
    @action(detail=True, methods=["get"])
    def balance(self, request, pk=None):
        wallet = self.get_object()
        return Response(
            {
                "balance": wallet.balance,
                "currency": "USD",  # You can make this configurable
            }
        )
