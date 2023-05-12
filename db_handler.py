import psycopg2
from psycopg2 import pool
from psycopg2 import sql

# Set up a connection pool with a minimum of 1 connection and a maximum of 5 connections
# to the PostgreSQL database named 'job_board', located on 'localhost' at port 5432
conn_pool = pool.SimpleConnectionPool(1, 5, database='job_board', host='localhost', port='5432')


def init_new_user(message):
    """
    Inserts a new user into the 'seen_jobs' table, if the user's ID does not already exist.
    :param message: Telegram message object
    """
    try:
        with conn_pool.getconn() as conn, conn.cursor() as cursor:
            # Create an SQL statement that inserts the user's ID into the 'seen_jobs' table,
            # ignoring the insert if the user's ID already exists
            insert_statement = sql.SQL("INSERT INTO seen_jobs(id) VALUES(%s) ON CONFLICT DO NOTHING")
            cursor.execute(insert_statement, [message.chat.id])

            # Commit the transaction
            conn.commit()

            # Close the cursor and return the connection to the connection pool
            cursor.close()
            conn_pool.putconn(conn)
    except psycopg2.Error as err:
        print('An error occurred: ', err)


def insert_into_settings(message, column):
    """
    Inserts a value for a specified column into the 'seen_jobs' table for a specified user ID.
    :param message: Telegram message object
    :param column: Name of the column in which to insert the value
    :return: A confirmation message string
    """
    try:
        with conn_pool.getconn() as conn, conn.cursor() as cursor:
            # Create an SQL statement that updates the specified column for the specified user ID
            insert_statement = sql.SQL("UPDATE seen_jobs SET {} = %s WHERE id = %s").format(sql.Identifier(column))

            # Execute the SQL statement, passing in the message text and chat ID as parameters
            cursor.execute(insert_statement, [message.text, message.chat.id])

            # Commit the transaction to the database
            conn.commit()

            # Close the cursor and return the connection to the connection pool
            cursor.close()
            conn_pool.putconn(conn)

            # Return a confirmation message string
            return f'Setting of {column} set to {message.text}'
    except psycopg2.Error as err:
        # If an error occurs, return an error message string
        return f"An error occurred: {err}"


def get_from_settings(user_id, *args):
    """
    Retrieves the values for one or more specified columns from the 'seen_jobs' table
    for a specified user ID.
    :param user_id: ID of the user whose settings to retrieve
    :param args: List of column names to retrieve values for
    :return: A tuple of the retrieved values
    """
    try:
        with conn_pool.getconn() as conn, conn.cursor() as cursor:
            # Create an SQL statement that selects the specified columns from the 'seen_jobs' table,
            # for the specified user ID
            get_statement = sql.SQL("SELECT {} FROM seen_jobs WHERE id = %s").format(
                sql.SQL(',').join(map(sql.Identifier, args)))

            # Execute the SQL statement, passing in the user ID as a parameter
            cursor.execute(get_statement, [user_id])

            # Fetch the first row of the result set
            result = cursor.fetchone()

            # Close the cursor and return the connection to the connection pool
            cursor.close()
            conn_pool.putconn(conn)

            return result

    except psycopg2.Error as err:
        print("An error occurred: ", err)