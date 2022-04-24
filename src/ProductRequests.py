from database.connection import Connector

class ProductRequests:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity

    def getProduct(self, name):
        query = "SELECT * FROM products WHERE name LIKE %s"
        data = (name,)
        db = Connector()
        db.execute(query, data)
        return db.fetch()


def executeQuery():
    productRequest = ProductRequests(1, 1)
    product = productRequest.getProduct("cereal")
    print(product)


executeQuery()