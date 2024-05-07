import mysql.connector
global cnx


# Now create connection to the  database

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="food_db"
)

def get_order_status(order_id: int):

    cursor = cnx.cursor()

    # SQL query
    query = ("SELECT status FROM order_tracking WHERE order_id = %s")

    # Now executing the query

    cursor.execute(query, (order_id,))

    # Get result

    result = cursor.fetchone()

    # Closing the cursor

    cursor.close()
    cnx.close()

    if result is not None:
            # Ensure that result is a tuple before accessing its elements
        if isinstance(result, tuple) and len(result) > 0:
            return result[0]
        else:
            print("Unexpected result format:", result)
            return None
    else:
        return None