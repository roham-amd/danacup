from django.contrib import admin
from .models import (
    CustomUser,
    Category,
    Color,
    Product,
    Comment,
    Wallet,
    Order,
    OrderItem,
    Payment,
    Discount,
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name",)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "discount_percent",
        "start_date",
        "end_date",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    date_hierarchy = "start_date"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "created_at")
    list_filter = ("category", "colors", "discount")
    search_fields = ("name", "description")
    filter_horizontal = ("colors",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("user__username", "product__name", "text")


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "created_at")
    search_fields = ("user__username",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "payment_status",
        "total_amount",
        "created_at",
    )
    list_filter = ("status", "payment_status")
    search_fields = ("user__username", "id")
    inlines = [OrderItemInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "amount",
        "payment_method",
        "status",
        "created_at",
    )
    list_filter = ("status", "payment_method")
    search_fields = ("order__id", "transaction_id")
