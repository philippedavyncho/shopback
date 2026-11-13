from django.db import models
from products.models import Product
class Promotion(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=40, unique=True, blank=True)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    products = models.ManyToManyField(Product, blank=True, related_name="promotions")
