import mysql.connector
from mysql.connector import Error

class DatabaseConnection:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self._connection = None
        self._cursor = None

    def connect(self):
        try:
            self._connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self._cursor = self._connection.cursor(dictionary=True)
            print("Conexão feita com sucesso.")
            return self
        except Error as e:
            print(f"Erro na conexão: {e}")
            raise

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            try:
                if exc_type:
                    print(f"Ocorreu um erro: {exc_type}. Revertendo...")
                    self._connection.rollback()
                else:
                    self._connection.commit()
            finally:
                if self._cursor:
                    self._cursor.close()
                self._connection.close()
                print("Conexão encerrada.")
    
    def execute_query(self, query, params=None):
        self._cursor.execute(query, params or ())
        
    def fetch_one(self, query, params=None):
        self.execute_query(query, params)
        return self._cursor.fetchone()
        
    def fetch_all(self, query, params=None):
        self.execute_query(query, params)
        return self._cursor.fetchall()