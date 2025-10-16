# alx_backend_graphql_crm/schema.py
import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation

class Query(CRMQuery, graphene.ObjectType):
    # you can add top-level fields here if needed
    pass

class Mutation(CRMMutation, graphene.ObjectType):
    # inherits CRM mutations
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
