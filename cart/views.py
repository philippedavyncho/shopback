from django.db import transaction
from rest_framework import permissions, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView
from inventory.models import Stock
from products.models import ProductVariant
from .models import Cart, CartItem
from .serializers import CartItemInputSerializer, CartSerializer, CartSyncSerializer

class CartConflict(APIException):
    status_code = 409
    default_detail = "Le panier ne peut pas être synchronisé."

class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_cart(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.prefetch_related("items__variant__product__images").get(pk=cart.pk)
    def get(self, request): return Response(CartSerializer(self.get_cart()).data)
    @transaction.atomic
    def put(self, request):
        data = CartSyncSerializer(data=request.data); data.is_valid(raise_exception=True)
        cart = self.get_cart()
        keep = []
        for item in data.validated_data["items"]:
            variant = ProductVariant.objects.select_related("product").filter(pk=item["variant_id"], is_active=True, product__status="active").first()
            if not variant: raise CartConflict("Une variante du panier n’est plus disponible.")
            stock = Stock.objects.select_for_update().filter(variant=variant).first()
            if not stock or stock.available < item["quantity"]:
                raise CartConflict(f"Stock insuffisant pour {variant.product.name}.")
            CartItem.objects.update_or_create(cart=cart, variant=variant, defaults={"quantity": item["quantity"]})
            keep.append(variant.id)
        cart.items.exclude(variant_id__in=keep).delete()
        return Response(CartSerializer(cart).data)
    @transaction.atomic
    def post(self, request):
        data = CartItemInputSerializer(data=request.data); data.is_valid(raise_exception=True)
        variant = ProductVariant.objects.select_related("product").filter(pk=data.validated_data["variant_id"], is_active=True, product__status="active").first()
        if not variant: return Response({"detail": "Variante indisponible."}, status=404)
        quantity = data.validated_data["quantity"]
        stock = Stock.objects.select_for_update().filter(variant=variant).first()
        if not stock or stock.available < quantity: return Response({"detail": "Stock insuffisant."}, status=409)
        cart = self.get_cart(); item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, defaults={"quantity": quantity})
        if not created:
            if stock.available < item.quantity + quantity: return Response({"detail": "Stock insuffisant."}, status=409)
            item.quantity += quantity; item.save(update_fields=["quantity"])
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
    @transaction.atomic
    def patch(self, request):
        data = CartItemInputSerializer(data=request.data); data.is_valid(raise_exception=True)
        variant_id, quantity = data.validated_data["variant_id"], data.validated_data["quantity"]
        cart = self.get_cart()
        item = CartItem.objects.filter(cart=cart, variant_id=variant_id).first()
        if not item: return Response({"detail": "Article absent du panier."}, status=404)
        stock = Stock.objects.select_for_update().filter(variant_id=variant_id).first()
        if not stock or stock.available < quantity: return Response({"detail": "Stock insuffisant."}, status=409)
        item.quantity = quantity; item.save(update_fields=["quantity"])
        return Response(CartSerializer(cart).data)
    def delete(self, request):
        item_id = request.query_params.get("item")
        variant_id = request.query_params.get("variant_id")
        if item_id: CartItem.objects.filter(cart=self.get_cart(), pk=item_id).delete()
        elif variant_id: CartItem.objects.filter(cart=self.get_cart(), variant_id=variant_id).delete()
        return Response(CartSerializer(self.get_cart()).data)
