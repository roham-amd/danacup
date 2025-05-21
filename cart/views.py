from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

# Create your views here.


class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing shopping carts.
    Provides endpoints for cart operations like adding items, removing items,
    updating quantities, and calculating totals.
    """

    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        tags=["cart"],
        summary="Add item to cart",
        description="Adds a product to the cart with specified quantity.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Cart ID"),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"},
                    "quantity": {"type": "integer", "minimum": 1},
                },
                "required": ["product_id"],
            }
        },
        responses={
            200: CartItemSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Cart or product not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response(
                {"error": "Product ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart_item = cart.add_item(product_id, quantity)
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["cart"],
        summary="Remove item from cart",
        description="Removes a specific item from the cart.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Cart ID"),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "integer"},
                },
                "required": ["item_id"],
            }
        },
        responses={
            200: OpenApiResponse(description="Item removed successfully"),
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Cart or item not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get("item_id")

        if not item_id:
            return Response(
                {"error": "Item ID is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart.remove_item(item_id)
            return Response({"message": "Item removed successfully"})
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["cart"],
        summary="Update item quantity",
        description="Updates the quantity of a specific item in the cart.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Cart ID"),
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "item_id": {"type": "integer"},
                    "quantity": {"type": "integer", "minimum": 1},
                },
                "required": ["item_id", "quantity"],
            }
        },
        responses={
            200: CartItemSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Cart or item not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def update_quantity(self, request, pk=None):
        cart = self.get_object()
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")

        if not item_id or not quantity:
            return Response(
                {"error": "Item ID and quantity are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart_item = cart.update_item_quantity(item_id, quantity)
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

    @extend_schema(
        tags=["cart"],
        summary="Clear cart",
        description="Removes all items from the cart.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Cart ID"),
        ],
        responses={
            200: OpenApiResponse(description="Cart cleared successfully"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Cart not found"),
        },
    )
    @action(detail=True, methods=["post"])
    def clear(self, request, pk=None):
        cart = self.get_object()
        cart.clear()
        return Response({"message": "Cart cleared successfully"})

    @extend_schema(
        tags=["cart"],
        summary="Get cart total",
        description="Calculates and returns the total price and number of items in the cart.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Cart ID"),
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "total": {"type": "number"},
                    "items_count": {"type": "integer"},
                },
            },
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Cart not found"),
        },
    )
    @action(detail=True, methods=["get"])
    def total(self, request, pk=None):
        cart = self.get_object()
        return Response(
            {"total": cart.get_total(), "items_count": cart.get_items_count()}
        )
