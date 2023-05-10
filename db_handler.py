import psycopg2
from psycopg2 import pool
from psycopg2 import sql


# Set up a connection pool
conn_pool = pool.SimpleConnectionPool(1, 5,
                                      database='job_board',
                                      host='localhost',
                                      port='5432')


# initialise user in database
def init_new_user(message):
    try:
        conn = conn_pool.getconn()
        cursor = conn.cursor()

        insert_statement = sql.SQL("INSERT INTO seen_jobs(id) VALUES(%s) ON CONFLICT DO NOTHING")
        cursor.execute(insert_statement, [message.chat.id])

        conn.commit()

    except psycopg2.Error as err:
        print('An error occured: ', err)


# insert into user's setting
def insert_into_settings(message, column):
    try:
        conn = conn_pool.getconn()
        cursor = conn.cursor()

        insert_statement = sql.SQL("UPDATE seen_jobs SET {} = %s WHERE id = %s").format(sql.Identifier(column))

        cursor.execute(insert_statement, [message.text, message.chat.id])

        conn.commit()
        cursor.close()
        conn_pool.putconn(conn)

        return f'Setting of {column} set to {message.text}'
    except psycopg2.Error as err:
        return f"An error occurred: {err}"


# get from user's settings
def get_from_settings(message, column):
    try:
        conn = conn_pool.getconn()
        cursor = conn.cursor()

        get_statement = sql.SQL("SELECT %s FROM seen_jobs WHERE id = %s")

        cursor.execute(get_statement, [column, message.chat.id])

        result = cursor.fetchall()
        cursor.close()
        conn_pool.putconn(conn)
        return result
    except psycopg2.Error as err:
        print("An error occurred: ", err)

