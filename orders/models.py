import uuid
from django.conf import settings
from django.db import models
from products.models import ProductVariant

def generate_order_number(): return uuid.uuid4().hex[:12].upper()

class Order(models.Model):
    class Status(models.TextChoices): PENDING = "pending", "En attente"; CONFIRMED = "confirmed", "Confirmée"; PROCESSING = "processing", "Préparation"; SHIPPED = "shipped", "Expédiée"; DELIVERED = "delivered", "Livrée"; CANCELLED = "cancelled", "Annulée"
    number = models.CharField(max_length=24, unique=True, default=generate_order_number)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    currency = models.CharField(max_length=3, default="XOF")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_address = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["-created_at"]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=64)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=12, decimal_places=2)
