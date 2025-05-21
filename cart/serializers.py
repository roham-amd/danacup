from rest_framework import serializers
from core.models import Cart, CartItem
from product.serializers import ProductSerializer, ColorSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "quantity",
            "color",
            "total_price",
            "created_at",
        ]
        read_only_fields = ["total_price"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price", "created_at", "updated_at"]
        read_only_fields = ["total_price"]
