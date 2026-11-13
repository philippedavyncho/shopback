from django.db import transaction
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from cart.models import Cart
from accounts.models import Address
from inventory.models import Stock, StockMovement
from payments.models import Payment
from shipping.services import calculate_shipping
from .models import Order, OrderItem
from .serializers import OrderSerializer, CheckoutSerializer
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "number"
    def get_queryset(self): return Order.objects.filter(user=self.request.user).prefetch_related("items")

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def checkout(self, request):
        data = CheckoutSerializer(data=request.data, context={"request": request}); data.is_valid(raise_exception=True)
        cart = Cart.objects.prefetch_related("items__variant__product").filter(user=request.user).first()
        if not cart or not cart.items.exists(): return Response({"detail": "Le panier est vide."}, status=400)
        address = Address.objects.get(pk=data.validated_data["address_id"], user=request.user)
        order = Order.objects.create(user=request.user,
            shipping_address={"recipient_name": address.recipient_name, "phone": address.phone, "line1": address.line1,
            "line2": address.line2, "city": address.city, "region": address.region, "postal_code": address.postal_code, "country": address.country})
        subtotal = 0
        for item in cart.items.all():
            stock = Stock.objects.select_for_update().filter(variant=item.variant).first()
            if not stock or stock.available < item.quantity:
                raise serializers.ValidationError({"detail": f"Stock insuffisant pour {item.variant.product.name}."})
            line_total = item.variant.price * item.quantity
            subtotal += line_total
            OrderItem.objects.create(order=order, variant=item.variant, product_name=item.variant.product.name,
                sku=item.variant.sku, unit_price=item.variant.price, quantity=item.quantity, line_total=line_total)
            stock.quantity -= item.quantity; stock.save(update_fields=["quantity", "updated_at"])
            StockMovement.objects.create(stock=stock, kind=StockMovement.Kind.OUT, quantity=item.quantity, reference=order.number)
        currencies = {item.variant.currency for item in cart.items.all()}
        if len(currencies) != 1:
            raise serializers.ValidationError({"detail": "Un panier doit utiliser une seule devise."})
        order.subtotal = subtotal; order.shipping_amount = calculate_shipping(address.country, subtotal)
        order.total = subtotal + order.shipping_amount
        order.currency = currencies.pop()
        order.save(update_fields=["subtotal", "shipping_amount", "total", "currency", "updated_at"])
        Payment.objects.create(order=order, method=data.validated_data["payment_method"], status=Payment.Status.PENDING,
                               amount=order.total, currency=order.currency)
        cart.items.all().delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
