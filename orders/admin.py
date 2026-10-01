from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = (
        "product", "product_name", "unit_price", "quantity", "subtotal_display",
    )

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj):
        return obj.subtotal if obj.pk else "-"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    list_editable = ("status",)
    search_fields = ("user__username", "=id")
    readonly_fields = ("user", "total", "created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product_name", "unit_price",
                    "quantity", "subtotal_display")
    search_fields = ("product_name", "order__user__username")
    readonly_fields = ("order", "product", "product_name",
                       "unit_price", "quantity")

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj):
        return obj.subtotal