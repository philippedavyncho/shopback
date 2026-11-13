from django.db import models
from orders.models import Order

class Payment(models.Model):
    class Status(models.TextChoices): PENDING = "pending", "En attente"; AUTHORIZED = "authorized", "Autorisée"; PAID = "paid", "Payée"; FAILED = "failed", "Échouée"; REFUNDED = "refunded", "Remboursée"
    class Method(models.TextChoices): COD = "cod", "Paiement à la livraison"; ORANGE = "orange_money", "Orange Money"; WAVE = "wave", "Wave"; OTHER = "other", "Autre"
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payments")
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="XOF")
    provider_reference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Provider secrets and card data must never be stored here.
