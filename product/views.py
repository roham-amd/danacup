from django.shortcuts import render
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Product, Category, Color, Discount
from .serializers import (
    ProductSerializer,
    ProductCreateUpdateSerializer,
    CategorySerializer,
    ColorSerializer,
    DiscountSerializer,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)

# Create your views here.


class DiscountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing discounts.
    """

    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        tags=["discounts"],
        summary="List discounts",
        description="Retrieves a list of all discounts.",
        responses={
            200: DiscountSerializer(many=True),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["discounts"],
        summary="Create discount",
        description="Creates a new discount.",
        request=DiscountSerializer,
        responses={
            201: DiscountSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    Supports filtering, searching, and ordering.
    """

    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "colors"]
    search_fields = ["name", "description"]
    ordering_fields = ["price", "created_at", "name"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        return ProductSerializer

    @extend_schema(
        tags=["products"],
        summary="List products",
        description="Retrieves a list of all products with their discount information.",
        responses={
            200: ProductSerializer(many=True),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["products"],
        summary="Retrieve product",
        description="Retrieves details of a specific product with its discount information.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Product ID"),
        ],
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Product not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["products"],
        summary="Create product",
        description="Creates a new product with optional discount.",
        request=ProductCreateUpdateSerializer,
        responses={
            201: ProductSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["products"],
        summary="Update product",
        description="Updates an existing product and its discount information.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Product ID"),
        ],
        request=ProductCreateUpdateSerializer,
        responses={
            200: ProductSerializer,
            400: OpenApiResponse(description="Invalid input data"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Product not found"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["products"],
        summary="Delete product",
        description="Deletes a product.",
        parameters=[
            OpenApiParameter(name="pk", type=int, description="Product ID"),
        ],
        responses={
            204: OpenApiResponse(description="Product deleted successfully"),
            401: OpenApiResponse(
                description="Authentication credentials were not provided."
            ),
            404: OpenApiResponse(description="Product not found"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["products"],
        summary="Get discounted products",
        description="Retrieves a list of all products that currently have active discounts.",
        responses={
            200: ProductSerializer(many=True),
        },
    )
    @action(detail=False, methods=["get"])
    def discounted(self, request):
        products = Product.objects.filter(discount__isnull=False)
        products = [p for p in products if p.has_active_discount]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories.
    Supports searching by name and description.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "description"]


class ColorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product colors.
    Supports searching by name.
    """

    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
