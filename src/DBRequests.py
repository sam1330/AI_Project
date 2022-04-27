from database.connection import Connector
from telegram.ext import *

class DBRequests:
    # Esta funcion obtiene los productos por nombre
    def getProductByName(self, name):
        query = "SELECT * FROM products WHERE name LIKE %s"
        data = (name,)
        db = Connector()
        db.execute(query, data)
        return db.fetch()

    # Esta funcion obtiene los productos por categoria
    def getProductsByCategory(self, category):
        query = "SELECT * FROM products WHERE category LIKE %s"
        data = (category,)
        db = Connector()
        db.execute(query, data)
        return db.fetch()
    
    # Esta funcion obtiene los productos por id
    def getProductById(self, client_id):
        query = "SELECT * FROM products WHERE id = %s"
        data = (client_id,)
        db = Connector()
        db.execute(query, data)
        return db.fetch()
    
    # Esta funcion obtiene los clientes
    def getClient(self, phone):
        query = "SELECT * FROM clients WHERE phone = %s"
        data = (phone,)
        db = Connector()
        db.execute(query, data)
        return db.fetch()

    # Esta funcion agrega los productos
    def addClient(self, name, email, phone):
        client = self.getClient(phone)
        if len(client) > 0:
          return client
        query = "INSERT INTO clients (name, email, phone) VALUES (%s, %s, %s)"
        data = (name, email, phone)
        db = Connector()
        db.execute(query, data)
        return self.getClient(phone)

    # Esta funcion es para completar la compra (Hacer la factura)
    def completePurchase(self, purchases_num, product_id, client_id, total, payment_type, status):
        query = "INSERT INTO purchases (purchase_num, product_id, client_id, total, payment_type, status) VALUES (%s, %s, %s, %s, %s, %s)"
        data = (purchases_num, product_id, client_id, total, payment_type, status)
        db = Connector()
        db.execute(query, data)

    # Esta funcion es para obtener el numero de la ultima factura hecha
    def getLastPurchaseNumber(self):
        query = "SELECT purchase_num FROM purchases ORDER BY purchase_num DESC LIMIT 1"
        db = Connector()
        db.execute(query)
        purchase_num = db.fetch()
        if len(purchase_num) > 0:
            return purchase_num[0][0]
        return 0

    def getOrderState(self, purchase_num):
        query = "SELECT status FROM purchases WHERE purchase_num = %s"
        data = (purchase_num,)
        db = Connector()
        db.execute(query, data)
        state = db.fetch()
        if len(state) > 0:
            return state[0][0]
        return "no existe"

