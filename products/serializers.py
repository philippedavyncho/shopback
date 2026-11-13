from rest_framework import serializers
from .models import Product, ProductImage, ProductVariant

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta: model = ProductImage; fields = ["id", "image", "alt_text", "position"]
class ProductVariantSerializer(serializers.ModelSerializer):
    available = serializers.SerializerMethodField()
    class Meta: model = ProductVariant; fields = ["id", "name", "sku", "attributes", "price", "compare_at_price", "currency", "available"]
    def get_available(self, obj):
        stock = getattr(obj, "stock", None)
        return stock.available if stock else 0
class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    brand_name = serializers.CharField(source="brand.name", read_only=True, allow_null=True)
    class Meta: model = Product; fields = ["id", "name", "slug", "description", "category", "category_name", "brand", "brand_name", "images", "variants", "created_at"]
