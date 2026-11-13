from django.db import models
from products.models import ProductVariant

class Stock(models.Model):
    variant = models.OneToOneField(ProductVariant, on_delete=models.CASCADE, related_name="stock")
    quantity = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def available(self): return max(0, self.quantity - self.reserved)

class StockMovement(models.Model):
    class Kind(models.TextChoices): IN = "in", "Entrée"; OUT = "out", "Sortie"; ADJUST = "adjust", "Ajustement"; RESERVE = "reserve", "Réservation"; RELEASE = "release", "Libération"
    stock = models.ForeignKey(Stock, on_delete=models.PROTECT, related_name="movements")
    kind = models.CharField(max_length=10, choices=Kind.choices)
    quantity = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
