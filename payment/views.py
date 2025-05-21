from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from core.models import Payment, Order, Transaction
from .serializers import PaymentSerializer
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

# Create your views here.


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payments.
    Provides endpoints for processing payments, refunds, cancellations,
    and checking payment status.
    """

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

    @extend_schema(
        tags=["payments"],
        summary="List payments",
        description="Retrieves a list of all payments for the authenticated user.",
        responses={
            200: PaymentSerializer(many=True),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["payments"],
        summary="Retrieve payment",
        description="Retrieves details of a specific payment.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Payment ID"),
        ],
        responses={
            200: PaymentSerializer,
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Payment not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["payments"],
        summary="Create payment",
        description="Creates a new payment record.",
        request=PaymentSerializer,
        responses={
            201: PaymentSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["payments"],
        summary="Update payment",
        description="Updates an existing payment record.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Payment ID"),
        ],
        request=PaymentSerializer,
        responses={
            200: PaymentSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Payment not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["payments"],
        summary="Delete payment",
        description="Deletes a payment record.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Payment ID"),
        ],
        responses={
            204: OpenApiResponse(description="Payment deleted successfully"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Payment not found"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["payments"],
        summary="Process payment",
        description="Processes a payment for an order using the specified payment method.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "integer"},
                    "payment_method": {
                        "type": "string",
                        "enum": ["wallet", "credit_card", "bank_transfer"],
                        "default": "wallet",
                    },
                },
                "required": ["order_id"],
            }
        },
        responses={
            201: PaymentSerializer,
            400: OpenApiResponse(
                description="Invalid input data or insufficient balance"
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Order not found"),
            501: OpenApiResponse(description="Payment method not implemented"),
        },
    )
    @action(detail=False, methods=["post"])
    def process_payment(self, request):
        order_id = request.data.get("order_id")
        payment_method = request.data.get("payment_method", "wallet")

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if order.payment_status == "paid":
            return Response(
                {"error": "Order is already paid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                if payment_method == "wallet":
                    # Process wallet payment
                    wallet = request.user.wallet
                    if wallet.balance < order.total_amount:
                        return Response(
                            {"error": "Insufficient wallet balance"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

                    # Create payment record
                    payment = Payment.objects.create(
                        order=order,
                        amount=order.total_amount,
                        payment_method="wallet",
                        status="completed",
                    )

                    # Process wallet transaction
                    wallet.withdraw(order.total_amount)

                    # Create transaction record
                    Transaction.objects.create(
                        wallet=wallet,
                        amount=order.total_amount,
                        transaction_type="purchase",
                        order=order,
                    )

                    # Update order status
                    order.payment_status = "paid"
                    order.save()

                    serializer = PaymentSerializer(payment)
                    return Response(
                        serializer.data, status=status.HTTP_201_CREATED
                    )

                elif payment_method == "credit_card":
                    # Here you would integrate with a credit card payment gateway
                    # For now, we'll just create a pending payment
                    payment = Payment.objects.create(
                        order=order,
                        amount=order.total_amount,
                        payment_method="credit_card",
                        status="pending",
                    )
                    return Response(
                        {"error": "Credit card payment not implemented"},
                        status=status.HTTP_501_NOT_IMPLEMENTED,
                    )

                elif payment_method == "bank_transfer":
                    # Here you would integrate with a bank transfer system
                    # For now, we'll just create a pending payment
                    payment = Payment.objects.create(
                        order=order,
                        amount=order.total_amount,
                        payment_method="bank_transfer",
                        status="pending",
                    )
                    return Response(
                        {"error": "Bank transfer payment not implemented"},
                        status=status.HTTP_501_NOT_IMPLEMENTED,
                    )

                else:
                    return Response(
                        {"error": "Unsupported payment method"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["payments"],
        summary="Refund payment",
        description="Processes a refund for a completed payment.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Payment ID"),
        ],
        responses={
            200: PaymentSerializer,
            400: OpenApiResponse(
                description="Payment cannot be refunded in its current status"
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Payment not found"),
            501: OpenApiResponse(description="Refund method not implemented"),
        },
    )
    @action(detail=True, methods=["post"])
    def refund(self, request, pk=None):
        payment = self.get_object()

        if payment.status != "completed":
            return Response(
                {"error": "Only completed payments can be refunded"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                if payment.payment_method == "wallet":
                    # Process wallet refund
                    wallet = request.user.wallet
                    wallet.deposit(payment.amount)

                    # Create refund transaction
                    Transaction.objects.create(
                        wallet=wallet,
                        amount=payment.amount,
                        transaction_type="refund",
                        order=payment.order,
                    )

                    # Update payment status
                    payment.status = "refunded"
                    payment.save()

                    # Update order status
                    order = payment.order
                    order.payment_status = "refunded"
                    order.save()

                    serializer = PaymentSerializer(payment)
                    return Response(serializer.data)

                elif payment.payment_method in [
                    "credit_card",
                    "bank_transfer",
                ]:
                    # Here you would integrate with the respective payment gateway
                    # For now, we'll just update the status
                    payment.status = "refunded"
                    payment.save()

                    order = payment.order
                    order.payment_status = "refunded"
                    order.save()

                    return Response(
                        {
                            "error": f"{payment.payment_method} refund not implemented"
                        },
                        status=status.HTTP_501_NOT_IMPLEMENTED,
                    )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["payments"],
        summary="Cancel payment",
        description="Cancels a pending payment.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Payment ID"),
        ],
        responses={
            200: PaymentSerializer,
            400: OpenApiResponse(
                description="Payment cannot be cancelled in its current status"
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Payment not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        payment = self.get_object()

        if payment.status not in ["pending"]:
            return Response(
                {"error": "Only pending payments can be cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payment.status = "failed"
            payment.save()

            order = payment.order
            order.payment_status = "failed"
            order.save()

            serializer = PaymentSerializer(payment)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["payments"],
        summary="Get payment status",
        description="Retrieves the current status and details of a payment.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Payment ID"),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "payment_method": {"type": "string"},
                    "amount": {"type": "number"},
                    "created_at": {"type": "string", "format": "date-time"},
                    "updated_at": {"type": "string", "format": "date-time"},
                },
            },
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Payment not found"),
        },
    )
    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        payment = self.get_object()
        return Response(
            {
                "status": payment.status,
                "payment_method": payment.payment_method,
                "amount": payment.amount,
                "created_at": payment.created_at,
                "updated_at": payment.updated_at,
            }
        )
