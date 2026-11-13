from django.db.models import Q
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Product
from .serializers import ProductSerializer
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "brand__name", "category__name"]
    ordering_fields = ["created_at", "variants__price", "name"]
    def get_queryset(self):
        qs = Product.objects.select_related("category", "brand").prefetch_related("images", "variants", "variants__stock")
        if not self.request.user.is_staff: qs = qs.filter(status=Product.Status.ACTIVE)
        category = self.request.query_params.get("category")
        if category: qs = qs.filter(category__slug=category)
        min_price, max_price = self.request.query_params.get("min_price"), self.request.query_params.get("max_price")
        if min_price: qs = qs.filter(variants__price__gte=min_price)
        if max_price: qs = qs.filter(variants__price__lte=max_price)
        return qs.distinct()
    def get_permissions(self): return [AllowAny()] if self.action in ("list", "retrieve") else [IsAdminUser()]
