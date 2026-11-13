from django.contrib import admin
from .models import Brand, Product, ProductImage, ProductVariant

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}

class ImageInline(admin.TabularInline): model = ProductImage; extra = 0
class VariantInline(admin.TabularInline): model = ProductVariant; extra = 0
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin): list_display = ("name", "category", "brand", "status", "created_at"); list_filter = ("status", "category", "brand"); search_fields = ("name", "variants__sku"); prepopulated_fields = {"slug": ("name",)}; inlines = [ImageInline, VariantInline]
