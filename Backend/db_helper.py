import mysql.connector
global cnx


# Now create connection to the  database

cnx = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password="root",
    database="food_db"
)


def insert_order_item(food_item, quantity, order_id):
    try:
        cursor = cnx.cursor()
        
        # calling the stored procedure form the database
        cursor.callproc('insert_order_item', (food_item, quantity, order_id))

        # Committing the changes
        cnx.commit()

        cursor.close()

        print("Order item inserted Successfully!")

        return 1
    
    except mysql.connector.Error as err:
        print(f"Error in inserting order item: {err}")

        # Rollback the changes
        cnx.rollback()

        return -1
    
    except Exception as e:
        print(f"An error occured: {e}")

        cnx.rollback()

        return -1
    


def insert_order_tracking(order_id, status):
    # To insert record in the order tracking table
    cursor = cnx.cursor()

    # Inserting the record into the order_tracking table
    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
    cursor.execute(insert_query, (order_id, status))

    # Committing the changes
    cnx.commit()

    # Closing the cursor
    cursor.close()




def get_total_order_price(order_id):
    cursor = cnx.cursor()

    # Executing the SQL query to get the total order price
    query = f"SELECT get_total_order_price({order_id})"

    cursor.execute(query)

    result = cursor.fetchone()

    cursor.close()

    return result



def get_next_order_id():
    cursor = cnx.cursor()

    # Executing the SQL query to get the next available order_id


    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)

    # fetching the results
    result = cursor.fetchone()

    # close the cursor
    cursor.close()

    # Now we have fetched the max order id
    # now return the next available order id
    if result is None:
        return 1
       
    else:
        return result 
       




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

    if result is not None:
            # Ensure that result is a tuple before accessing its elements
        if isinstance(result, tuple) and len(result) > 0:
            return result[0]
        else:
            print("Unexpected result format:", result)
            return None
    else:
        return None