import mysql.connector
from utils.encryption import decrypt_results  # Assuming decrypt is a separate utility

def execute_sql(connection, sql):
    """
    Executes an SQL query on the given database connection and returns the decrypted results.

    :param connection: The active database connection (mysql.connector.connection.MySQLConnection)
    :param sql: The SQL query to be executed (str)
    :return: Decrypted results from the query (list of dicts)
    """
    try:
        # Create a cursor to interact with the database
        cursor = connection.cursor(dictionary=True)

        # Execute the SQL query
        cursor.execute(sql)

        # Fetch all the results from the query
        results = cursor.fetchall()

        # Close the cursor after the operation is complete
        cursor.close()

        # Return decrypted results
        return decrypt_results(results)

    except mysql.connector.Error as err:
        # Handle database connection errors
        print(f"Error executing SQL query: {err}")
        return None

    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {e}")
        return None
