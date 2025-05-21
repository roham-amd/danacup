from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    CategoryViewSet,
    ColorViewSet,
    DiscountViewSet,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"categories", CategoryViewSet)
router.register(r"colors", ColorViewSet)
router.register(r"discounts", DiscountViewSet, basename="discount")

urlpatterns = [
    path("", include(router.urls)),
]
