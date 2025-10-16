# seed_db.py
import os
import django
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

def run():
    # Clear simple demo data (careful on prod)
    print("Deleting existing demo data (customers, products, orders)...")
    Order.objects.all().delete()
    Customer.objects.all().delete()
    Product.objects.all().delete()

    # Create customers
    c1 = Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
    c2 = Customer.objects.create(name="Bob", email="bob@example.com", phone="123-456-7890")
    print("Created customers:", c1, c2)

    # Create products
    p1 = Product.objects.create(name="Laptop", price=Decimal("999.99"), stock=10)
    p2 = Product.objects.create(name="Mouse", price=Decimal("25.50"), stock=100)
    p3 = Product.objects.create(name="Keyboard", price=Decimal("45.00"), stock=50)
    print("Created products:", p1, p2, p3)

    # Create an order
    order = Order.objects.create(customer=c1, total_amount=Decimal("0.00"))
    order.products.set([p1, p2])
    order.recalc_total()
    print("Created order:", order, "total:", order.total_amount)

if __name__ == "__main__":
    run()
    print("Seed complete.")
