from rest_framework import serializers
from .models import Order, OrderItem
from accounts.models import Address
from payments.models import Payment
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta: model = OrderItem; fields = ["product_name", "sku", "unit_price", "quantity", "line_total"]
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta: model = Order; fields = ["number", "status", "currency", "subtotal", "shipping_amount", "total", "items", "created_at"]

class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.Method.choices, default=Payment.Method.COD)
    def validate_address_id(self, value):
        if not Address.objects.filter(pk=value, user=self.context["request"].user).exists():
            raise serializers.ValidationError("Adresse de livraison invalide.")
        return value
    def validate_payment_method(self, value):
        if value != Payment.Method.COD:
            raise serializers.ValidationError("Ce moyen de paiement n’est pas encore activé.")
        return value
