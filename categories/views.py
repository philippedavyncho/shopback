from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Category
from .serializers import CategorySerializer
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    lookup_field = "slug"
    def get_queryset(self): return Category.objects.filter(is_active=True).select_related("parent")
    def get_permissions(self): return [AllowAny()] if self.action in ("list", "retrieve") else [IsAdminUser()]
