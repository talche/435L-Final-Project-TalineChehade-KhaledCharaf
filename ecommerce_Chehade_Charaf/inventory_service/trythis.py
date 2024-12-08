import pymysql

connection = pymysql.connect(
    host='localhost',
    user='taline',
    password='Mitache28',
    database='ecommerce',
    port=3306
)

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT DATABASE();")
        result = cursor.fetchone()
        print(f"Connected to database: {result}")
finally:
    connection.close()
