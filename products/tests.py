from rest_framework.test import APITestCase
from categories.models import Category
from products.models import Product, ProductVariant

class CatalogApiTests(APITestCase):
    def test_public_catalog_only_returns_active_products(self):
        category = Category.objects.create(name="Maison")
        Product.objects.create(name="Lampe", category=category, status=Product.Status.ACTIVE)
        Product.objects.create(name="Brouillon", category=category, status=Product.Status.DRAFT)
        response = self.client.get("/api/v1/products/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["name"], "Lampe")

    def test_public_product_includes_variant_stock(self):
        category = Category.objects.create(name="Cuisine")
        product = Product.objects.create(name="Bol", category=category, status=Product.Status.ACTIVE)
        ProductVariant.objects.create(product=product, name="Bleu", sku="BOL-BLEU", price="1200.00")
        response = self.client.get("/api/v1/products/bol/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["variants"][0]["available"], 0)
