import psycopg2
from psycopg2 import Error


class DatabaseConnection:
    def __init__(self):
        self.host = "localhost"
        self.port = "5432"
        self.database = "pfe_db"
        self.user = "postgres"
        self.password = "ikramzalani2003"

    def connect(self):
        try:
            connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            return connection
        except Error as e:
            print("Erreur de connexion à PostgreSQL :", e)
            return None

    def verify_user(self, username, password):
        connection = self.connect()
        if connection is None:
            return False

        try:
            cursor = connection.cursor()
            query = """
                SELECT * FROM utilisateurs
                WHERE username = %s AND password = %s
            """
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            cursor.close()
            connection.close()

            return user is not None

        except Error as e:
            print("Erreur lors de la vérification utilisateur :", e)
            return False