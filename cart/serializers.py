from rest_framework import serializers
from .models import Cart, CartItem
from products.models import ProductVariant
from inventory.models import Stock

class CartItemInputSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, max_value=50)
class CartSyncSerializer(serializers.Serializer):
    items = CartItemInputSerializer(many=True, allow_empty=True)
    def validate_items(self, items):
        identifiers = [item["variant_id"] for item in items]
        if len(identifiers) != len(set(identifiers)):
            raise serializers.ValidationError("Chaque variante ne peut apparaître qu’une fois.")
        return items
class CartItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="variant.product.name", read_only=True)
    price = serializers.DecimalField(source="variant.price", max_digits=12, decimal_places=2, read_only=True)
    sku = serializers.CharField(source="variant.sku", read_only=True)
    slug = serializers.CharField(source="variant.product.slug", read_only=True)
    currency = serializers.CharField(source="variant.currency", read_only=True)
    image = serializers.SerializerMethodField()
    def get_image(self, obj):
        product_image = next(iter(obj.variant.product.images.all()), None)
        if not product_image:
            return ""
        url = product_image.image.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url
    class Meta: model = CartItem; fields = ["id", "variant", "name", "slug", "sku", "price", "currency", "quantity", "image"]
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta: model = Cart; fields = ["id", "items", "updated_at"]
