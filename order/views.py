from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

# Create your views here.


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing orders.
    Provides endpoints for creating orders from cart, cancelling orders,
    processing payments, and viewing order details.
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=["orders"],
        summary="Create order from cart",
        description="Creates a new order from the items in the user's cart.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "shipping_address": {"type": "string"},
                },
            }
        },
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(description="Cart is empty or invalid data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    @action(detail=False, methods=["post"])
    def create_from_cart(self, request):
        cart = request.user.cart
        if not cart.items.exists():
            return Response(
                {"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.create(
                user=request.user,
                total_amount=cart.get_total(),
                shipping_address=request.data.get("shipping_address", ""),
            )

            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                )

            # Clear the cart
            cart.clear()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["orders"],
        summary="Cancel order",
        description="Cancels an existing order and refunds the payment if applicable.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Order ID"),
        ],
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(
                description="Order cannot be cancelled in its current status"
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Order not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status not in ["pending", "processing"]:
            return Response(
                {"error": "Order cannot be cancelled in its current status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order.status = "cancelled"
            order.save()

            # Refund to wallet if payment was made
            if order.payment_status == "paid":
                wallet = request.user.wallet
                wallet.deposit(order.total_amount)

            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["orders"],
        summary="Pay for order",
        description="Processes payment for an order using the user's wallet balance.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Order ID"),
        ],
        responses={
            200: OrderSerializer,
            400: OpenApiResponse(
                description="Order is already paid or insufficient wallet balance"
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Order not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        order = self.get_object()

        if order.payment_status == "paid":
            return Response(
                {"error": "Order is already paid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            wallet = request.user.wallet
            if wallet.balance < order.total_amount:
                return Response(
                    {"error": "Insufficient wallet balance"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Process payment
            wallet.withdraw(order.total_amount)
            order.payment_status = "paid"
            order.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["orders"],
        summary="Get order items",
        description="Retrieves all items in a specific order.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Order ID"),
        ],
        responses={
            200: OrderItemSerializer(many=True),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Order not found"),
        },
    )
    @action(detail=True, methods=["get"])
    def items(self, request, pk=None):
        order = self.get_object()
        items = OrderItem.objects.filter(order=order)
        serializer = OrderItemSerializer(items, many=True)
        return Response(serializer.data)


class WalletDetailView(generics.RetrieveAPIView):
    """
    View for retrieving wallet details.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.wallet


class WalletDepositView(generics.CreateAPIView):
    """
    View for depositing funds into the wallet.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        amount = request.data.get("amount")
        if not amount or amount <= 0:
            return Response(
                {"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            wallet = request.user.wallet
            wallet.deposit(amount)
            return Response({"balance": wallet.balance})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class WalletWithdrawView(generics.CreateAPIView):
    """
    View for withdrawing funds from the wallet.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        amount = request.data.get("amount")
        if not amount or amount <= 0:
            return Response(
                {"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            wallet = request.user.wallet
            if wallet.balance < amount:
                return Response(
                    {"error": "Insufficient balance"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            wallet.withdraw(amount)
            return Response({"balance": wallet.balance})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class TransactionListView(generics.ListAPIView):
    """
    View for listing wallet transactions.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.wallet.transactions.all()
