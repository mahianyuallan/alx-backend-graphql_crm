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
