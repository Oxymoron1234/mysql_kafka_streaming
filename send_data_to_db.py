import mysql.connector
import time
from datetime import datetime
from config import *
import random
from config import *
def store_data(name, category, price):
    rows = ""
    try:
        connection = mysql.connector.connect(
            host = mysql_config['host'], 
            user = mysql_config['user'], 
            password = mysql_config['password'],
            database = mysql_config['database']
        )
        cursor = connection.cursor(dictionary=True)
        query = "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)"
        values = (name, category, price)
        cursor.execute(query,values)
        connection.commit()
        print(f"Inserted record with ID: {cursor.lastrowid}")
    except Exception as e:
        print (f"Error ---- {e}")
    finally:
        cursor.close()
        connection.close()

cat = ['Clothing','Book','Toy','Home','Electronics']

for i in range(1,200):
    index = random.randint(0,4)
    name = 'Product ' + str(i)
    category = cat[index]
    price = round(random.uniform(40, 200),2)
    store_data(name, category, price)
    time.sleep(1)
   