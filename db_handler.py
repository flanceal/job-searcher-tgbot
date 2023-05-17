import psycopg2
from psycopg2 import pool
from psycopg2 import sql


# Set up a connection pool with a minimum of 1 connection and a maximum of 5 connections
# to the PostgreSQL database named 'job_board', located on 'localhost' at port 5432
conn_pool = pool.SimpleConnectionPool(1, 5, database='job_board', host='localhost', port='5432')


def init_new_user(message):
    """
    Inserts a new user into the 'users_settings' table, if the user's ID does not already exist.
    :param message: Telegram message object
    """
    try:
        with conn_pool.getconn() as conn, conn.cursor() as cursor:
            # Create an SQL statement that inserts the user's ID into the 'users_settings' table,
            # ignoring the insert if the user's ID already exists
            insert_statement = sql.SQL("INSERT INTO users_settings(id) VALUES(%s) ON CONFLICT DO NOTHING")
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
    Inserts a value for a specified column into the 'users_settings' table for a specified user ID.
    :param message: Telegram message object
    :param column: Name of the column in which to insert the value
    :return: A confirmation message string
    """
    try:
        with conn_pool.getconn() as conn, conn.cursor() as cursor:
            # Create an SQL statement that updates the specified column for the specified user ID
            insert_statement = sql.SQL("UPDATE users_settings SET {} = %s WHERE id = %s").format(sql.Identifier(column))

            # Execute the SQL statement, passing in the message text and chat ID as parameters
            cursor.execute(insert_statement, [message.text, message.chat.id])

            # Commit the transaction to the database
            conn.commit()

            # Close the cursor and return the connection to the connection pool
            cursor.close()
            conn_pool.putconn(conn)

            # Return a confirmation message string
            return f'{column} is set to {message.text}'
    except psycopg2.Error as err:
        # If an error occurs, return an error message string
        return f"An error occurred: {err}"


def insert_seen_job(chat_id, title, specialisation, company, experience, location, link):
    """Inserts a new row into the seen_jobs table with the provided data.

        Args:
            chat_id (int): The ID of the user who saw the job.
            title (str): The title of the job.
            company (str): The name of the company offering the job.
            experience (str): The required experience level for the job.
            location (str): The location of the job.
            link (str): The URL link to the job posting.

        Returns:
            str: An error message string if an error occurs, otherwise returns None.
        """
    try:
        with conn_pool.getconn() as conn, conn.cursor() as cursor:
            # Create an SQL statement that inserts a new row into the seen_jobs table
            sql_statement = sql.SQL("INSERT INTO seen_jobs(user_id, title, specialisation, "
                                    "company, experience, location, link) "
                                    "VALUES (%s, %s, %s, %s, %s, %s, %s)")

            # Execute the SQL statement with the given parameters
            cursor.execute(sql_statement, (chat_id, title, specialisation, company, experience, location, link))

            # Commit the transaction to the database
            conn.commit()

            # Close the cursor and return the connection to the connection pool
            cursor.close()
            conn_pool.putconn(conn)
    except psycopg2.Error as err:
        # If an error occurs, return an error message string
        return f"An error occurred: {err}"


def get_from_settings(user_id, *args):
    """
    Retrieves the values for one or more specified columns from the 'users_settings' table
    for a specified user ID.
    :param user_id: ID of the user whose settings to retrieve
    :param args: List of column names to retrieve values for
    :return: A tuple of the retrieved values
    """
    try:
        with conn_pool.getconn() as conn, conn.cursor() as cursor:
            # Create an SQL statement that selects the specified columns from the 'users_settings' table,
            # for the specified user ID
            get_statement = sql.SQL("SELECT {} FROM users_settings WHERE id = %s").format(
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


def get_jobs(chat_id, specialisation):
    """
    Retrieve jobs from the seen_jobs table for a specific user and specialisation.

    Args:
        chat_id (int): The ID of the chat/user.
        specialisation (str): The specialisation of the jobs.

    Returns:
        list: A list of job records matching the user and specialisation.

    Raises:
        psycopg2.Error: If an error occurs while executing the SQL statement.
    """
    try:
        with conn_pool.getconn() as conn, conn.cursor() as cursor:
            # Create an SQL statement that selects the specified columns from the 'seen_jobs' table,
            # for the specified user ID and specialisation
            get_statement = sql.SQL("SELECT title, company, experience, location, link FROM seen_jobs "
                                    "WHERE user_id = %s AND specialisation = %s")

            # Execute the SQL statement, passing in the user ID and specialisation as parameters
            cursor.execute(get_statement, [chat_id, specialisation])

            # Fetch all rows of the result set
            results = cursor.fetchall()

            # Close the cursor and return the connection to the connection pool
            cursor.close()
            conn_pool.putconn(conn)

            return results

    except psycopg2.Error as err:
        print("An error occurred: ", err)
