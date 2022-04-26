import mysql.connector
# Esta es la clase que utilizamos para conectarnos a la base de datos. 
class Connector:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="ai_db"
        )
        self.cursor = self.connection.cursor(buffered=True)

    def execute(self, query, data=None):
        if data:
            self.cursor.execute(query, data)
        else:
            self.cursor.execute(query)
        self.connection.commit()

    def fetch(self):
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.connection.close()