import graphene
from crm.models import Product

class ProductType(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    stock = graphene.Int()

class UpdateLowStockProducts(graphene.Mutation):
    success = graphene.Boolean()
    updated_products = graphene.List(ProductType)

    def mutate(self, info):
        low_stock = Product.objects.filter(stock__lt=10)
        updated_products = []
        for product in low_stock:
            product.stock += 10
            product.save()
            updated_products.append(product)
        return UpdateLowStockProducts(success=True, updated_products=updated_products)

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

class Query(graphene.ObjectType):
    customers_count = graphene.Int()
    orders_count = graphene.Int()
    total_revenue = graphene.Float()

    def resolve_customers_count(root, info):
        return Customer.objects.count()

    def resolve_orders_count(root, info):
        return Order.objects.count()

    def resolve_total_revenue(root, info):
        return sum(order.total_amount for order in Order.objects.all())
