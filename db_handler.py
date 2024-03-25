import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mahesh",
    database="environment"
)

def get_next_order_id():
    cursor= cnx.cursor()

    query = "SELECT MAX(order_id) FROM user_carbon_footprints"
    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    if result is None:
        return 1
    else:
        return result+1