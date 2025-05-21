from rest_framework import serializers
from core.models import Category, Color, Product, Comment, Discount


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name", "code"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            "id",
            "name",
            "description",
            "discount_percent",
            "start_date",
            "end_date",
            "is_active",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ProductSerializer(serializers.ModelSerializer):
    discounted_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    has_active_discount = serializers.BooleanField(read_only=True)
    discount = DiscountSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    colors = ColorSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "discounted_price",
            "has_active_discount",
            "discount",
            "image",
            "category",
            "colors",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "image",
            "category",
            "colors",
            "discount",
        ]


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Comment
        fields = ["id", "user", "text", "rating", "created_at"]
        read_only_fields = ["user"]
