from django.db import models
from orders.models import Order
class Shipment(models.Model):
    class Status(models.TextChoices): PENDING = "pending", "En attente"; IN_TRANSIT = "in_transit", "En transit"; DELIVERED = "delivered", "Livrée"; RETURNED = "returned", "Retournée"
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="shipment")
    carrier = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
