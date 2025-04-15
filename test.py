import mysql.connector

config = {
    "user": "mysqluser",
    "password": "*7E567C9DC06217268D72D52BABCA14EAB8993ACF",
    "host": "104.237.2.219",
    "port": "5340",
    "database": "customer_db"
}

test= mysql.connector.connect(**config)
if test.is_connected():
    print("✅ Connection successful!")