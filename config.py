import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establishes a MySQL database connection."""
    try:
        conn = mysql.connector.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME")
        )
        print("✅ Database connection successful!")
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return None