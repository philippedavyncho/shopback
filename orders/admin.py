from django.contrib import admin
from .models import Order, OrderItem
class ItemInline(admin.TabularInline): model = OrderItem; extra = 0; readonly_fields = ("variant", "product_name", "sku", "unit_price", "quantity", "line_total")
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin): list_display = ("number", "user", "status", "total", "currency", "created_at"); list_filter = ("status", "created_at"); search_fields = ("number", "user__email"); inlines = [ItemInline]
