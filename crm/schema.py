# crm/schema.py
import re
from decimal import Decimal
from typing import List

import graphene
from graphene_django.filter import DjangoFilterConnectionField

from graphene import Field, List as GQLList, String, Int, Float
from graphene_django import DjangoObjectType
from django.db import transaction, IntegrityError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import Customer, Product, Order

# ----------------------------
# Types
# ----------------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# ----------------------------
# Input Types
# ----------------------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int(required=False)

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime(required=False)  # optional override (not used in this implementation)


# ----------------------------
# Helper Validation Functions
# ----------------------------
PHONE_REGEXES = [
    re.compile(r"^\+\d{7,15}$"),            # +1234567890...
    re.compile(r"^\d{3}-\d{3}-\d{4}$"),     # 123-456-7890
    re.compile(r"^\d{7,15}$"),              # simple digits 7-15 long
]

def is_valid_phone(phone: str) -> bool:
    if not phone:
        return True
    phone = phone.strip()
    return any(regex.match(phone) for regex in PHONE_REGEXES)


# ----------------------------
# Mutations
# ----------------------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        name = input.get("name").strip()
        email = input.get("email").strip()
        phone = input.get("phone", None)

        errors = []

        # Validate email format
        try:
            validate_email(email)
        except DjangoValidationError:
            errors.append("Invalid email format.")
            return CreateCustomer(customer=None, message="Validation failed.", errors=errors)

        # Validate phone
        if phone and not is_valid_phone(phone):
            errors.append("Invalid phone format. Accepts +1234567890, 123-456-7890, or digits.")
            return CreateCustomer(customer=None, message="Validation failed.", errors=errors)

        # Ensure unique email
        if Customer.objects.filter(email__iexact=email).exists():
            errors.append("Email already exists.")
            return CreateCustomer(customer=None, message="Email already exists.", errors=errors)

        try:
            customer = Customer.objects.create(name=name, email=email, phone=phone)
            return CreateCustomer(customer=customer, message="Customer created successfully.", errors=[])
        except Exception as e:
            return CreateCustomer(customer=None, message="Error creating customer.", errors=[str(e)])


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input: List[dict]):
        created_customers = []
        errors = []

        # Use a transaction but allow partial success by handling per-record errors
        # We'll use savepoints so failing one doesn't rollback others
        for idx, item in enumerate(input, start=1):
            name = (item.get("name") or "").strip()
            email = (item.get("email") or "").strip()
            phone = item.get("phone", None)

            record_identifier = f"record #{idx} (email: {email})"

            # Basic validations
            if not name or not email:
                errors.append(f"{record_identifier}: name and email are required.")
                continue

            try:
                validate_email(email)
            except DjangoValidationError:
                errors.append(f"{record_identifier}: invalid email format.")
                continue

            if phone and not is_valid_phone(phone):
                errors.append(f"{record_identifier}: invalid phone format.")
                continue

            if Customer.objects.filter(email__iexact=email).exists():
                errors.append(f"{record_identifier}: email already exists.")
                continue

            try:
                with transaction.atomic():
                    c = Customer.objects.create(name=name, email=email, phone=phone)
                    created_customers.append(c)
            except IntegrityError as ie:
                errors.append(f"{record_identifier}: integrity error - {str(ie)}")
            except Exception as e:
                errors.append(f"{record_identifier}: unexpected error - {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        name = (input.get("name") or "").strip()
        price = input.get("price")
        stock = input.get("stock", 0)

        errors = []
        if not name:
            errors.append("Product name is required.")
        try:
            price = Decimal(price)
        except Exception:
            errors.append("Invalid price format.")
            return CreateProduct(product=None, errors=errors)

        if price <= 0:
            errors.append("Price must be positive.")
        if stock is None:
            stock = 0
        try:
            stock = int(stock)
            if stock < 0:
                errors.append("Stock cannot be negative.")
        except Exception:
            errors.append("Stock must be an integer.")

        if errors:
            return CreateProduct(product=None, errors=errors)

        try:
            product = Product.objects.create(name=name, price=price, stock=stock)
            return CreateProduct(product=product, errors=[])
        except Exception as e:
            return CreateProduct(product=None, errors=[str(e)])


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    @staticmethod
    def mutate(root, info, input):
        customer_id = input.get("customer_id")
        product_ids = input.get("product_ids") or []

        errors = []

        # Validate customer
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID.")
            return CreateOrder(order=None, errors=errors)
        except Exception:
            errors.append("Invalid customer ID.")
            return CreateOrder(order=None, errors=errors)

        # Validate product ids presence
        if not product_ids:
            errors.append("At least one product must be selected.")
            return CreateOrder(order=None, errors=errors)

        # Resolve products and validate all exist
        products_qs = Product.objects.filter(pk__in=product_ids)
        found_ids = set(str(p.id) for p in products_qs)
        requested_ids = set(str(pid) for pid in product_ids)
        missing = requested_ids - found_ids
        if missing:
            errors.append(f"Invalid product ID(s): {', '.join(sorted(missing))}")
            return CreateOrder(order=None, errors=errors)

        # Calculate total_amount
        total = sum((p.price for p in products_qs), Decimal("0.00"))

        try:
            with transaction.atomic():
                order = Order.objects.create(customer=customer, total_amount=total)
                order.products.set(list(products_qs))
                # ensure total amount is consistent (recalc using related products)
                order.recalc_total()
                return CreateOrder(order=order, errors=[])
        except Exception as e:
            return CreateOrder(order=None, errors=[str(e)])


# ----------------------------
# Root Mutation & Query
# ----------------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    # allow reuse in project-level schema by importing Query from this module
    hello = graphene.String(default_value="Hello, GraphQL!")
    customers = GQLList(CustomerType)
    products = GQLList(ProductType)
    orders = GQLList(OrderType)

    def resolve_customers(root, info):
        return Customer.objects.all()

    def resolve_products(root, info):
        return Product.objects.all()

    def resolve_orders(root, info):
        return Order.objects.all()
