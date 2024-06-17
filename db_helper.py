import mysql.connector


def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="dessert_junky"
    )


def insert_order_item(food_item, quantity, order_id):
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))
        cnx.commit()
        print("Order item inserted successfully!")
        return 1
    except mysql.connector.Error as err:
        print(f"Error inserting order item: {err}")
        if cnx:
            cnx.rollback()
        return -1
    except Exception as e:
        print(f"An error occurred: {e}")
        if cnx:
            cnx.rollback()
        return -1
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()



def insert_order_tracking(order_id, status):
    cnx = None
    cursor = None
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        cursor.execute(insert_query, (order_id, status))
        cnx.commit()
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()


def get_next_order_id():
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        query = "SELECT MAX(order_id) + 1 FROM orders"
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 1
    finally:
        cursor.close()
        cnx.close()


def get_total_order_price(order_id):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        query = "SELECT SUM(total_price) FROM orders WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0
    finally:
        cursor.close()
        cnx.close()


def get_order_status(order_id):
    cnx = get_db_connection()
    cursor = cnx.cursor()
    try:
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        cursor.execute(query, (order_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        cursor.close()
        cnx.close()




if __name__ == "__main__":

    pass
