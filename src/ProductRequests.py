from database.connection import Connector
from telegram.ext import *

class ProductRequests:
    def getProductByName(self, name):
        query = "SELECT * FROM products WHERE name LIKE %s"
        data = (name,)
        db = Connector()
        db.execute(query, data)
        return db.fetch()

    def getProductsByCategory(self, category):
        query = "SELECT * FROM products WHERE category LIKE %s"
        data = (category,)
        db = Connector()
        db.execute(query, data)
        return db.fetch()
    
    def getClient(self, phone):
        query = "SELECT * FROM clients WHERE phone = %s"
        data = (phone,)
        db = Connector()
        db.execute(query, data)
        return db.fetch()

    def addClient(self, name, email, phone):
        client = self.getClient(phone)
        if len(client) > 0:
          return client
        query = "INSERT INTO clients (name, email, phone) VALUES (%s, %s, %s)"
        data = (name, email, phone)
        db = Connector()
        db.execute(query, data)
        return self.getClient(phone)

    def main(self, update):
        endConversation = False
        product = self.getProduct(update.message.text)
        if(len(product) == 0):
            update.message.reply_text("No se encontró el producto")
            endConversation = True
        else:
            update.message.reply_text("Tenemos disponible")
            update.message.reply_text("¿Cuántos deseas?")
            endConversation = True

def executeQuery():
    productRequest = ProductRequests(1, 1)
    product = productRequest.getProduct("cereal")
    print(product)
