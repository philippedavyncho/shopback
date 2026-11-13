from decimal import Decimal
from django.test import override_settings
from rest_framework.test import APITestCase
from accounts.models import Address, User
from categories.models import Category
from cart.models import Cart, CartItem
from inventory.models import Stock
from orders.models import Order
from payments.models import Payment
from products.models import Product, ProductVariant

class CheckoutApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="buyer@example.test", username="buyer", password="long-password-123")
        self.address = Address.objects.create(user=self.user, recipient_name="Buyer Test", phone="770000000", line1="1 rue du Marché", city="Dakar")
        category = Category.objects.create(name="Accessoires")
        product = Product.objects.create(name="Sac", slug="sac", category=category, status=Product.Status.ACTIVE)
        self.variant = ProductVariant.objects.create(product=product, name="Sable", sku="SAC-SABLE", price="25000.00")
        self.stock = Stock.objects.create(variant=self.variant, quantity=4)
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, variant=self.variant, quantity=2)
        self.client.force_authenticate(user=self.user)

    def test_checkout_records_cod_due_and_updates_stock_atomically(self):
        response = self.client.post("/api/v1/orders/checkout/", {"address_id": self.address.id, "payment_method": "cod"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.get().total, Decimal("50000.00"))
        payment = Payment.objects.get()
        self.assertEqual(payment.method, Payment.Method.COD)
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.stock.refresh_from_db()
        self.assertEqual(self.stock.quantity, 2)
        self.assertFalse(CartItem.objects.exists())

    def test_checkout_rejects_unavailable_online_payment(self):
        response = self.client.post("/api/v1/orders/checkout/", {"address_id": self.address.id, "payment_method": "wave"}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Order.objects.exists())

    @override_settings(SHIPPING_FLAT_RATE=Decimal("1200.00"))
    def test_shipping_is_calculated_on_server_not_taken_from_request(self):
        response = self.client.post("/api/v1/orders/checkout/", {"address_id": self.address.id, "shipping_amount": "0.00"}, format="json")
        self.assertEqual(response.status_code, 201)
        order = Order.objects.get()
        self.assertEqual(order.shipping_amount, Decimal("1200.00"))
        self.assertEqual(order.total, Decimal("51200.00"))

    def test_cart_sync_rolls_back_all_items_when_any_item_lacks_stock(self):
        product = Product.objects.create(name="Lampe", slug="lampe", category=self.variant.product.category, status=Product.Status.ACTIVE)
        variant = ProductVariant.objects.create(product=product, name="Ivoire", sku="LAMPE-IVOIRE", price="9000.00")
        Stock.objects.create(variant=variant, quantity=0)
        response = self.client.put("/api/v1/cart/", {"items": [
            {"variant_id": self.variant.id, "quantity": 3}, {"variant_id": variant.id, "quantity": 1},
        ]}, format="json")
        self.assertEqual(response.status_code, 409)
        self.assertEqual(CartItem.objects.get(variant=self.variant).quantity, 2)
        self.assertFalse(CartItem.objects.filter(variant=variant).exists())
