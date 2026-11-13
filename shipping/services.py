from decimal import Decimal
from django.conf import settings
from rest_framework.exceptions import ValidationError

def calculate_shipping(country: str, subtotal: Decimal) -> Decimal:
    """Use the server-owned configured flat rate until regional rules are defined."""
    if settings.SHIPPING_FLAT_RATE is None:
        raise ValidationError({"detail": "Les frais de livraison ne sont pas configurés."})
    return settings.SHIPPING_FLAT_RATE
