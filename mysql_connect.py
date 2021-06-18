from mysql.connector import MySQLConnection, Error
from mysql_dbconfig import read_db_config

""" Connect to MySQL database """
db_config = read_db_config()
connect = None
try:
    print('Connecting to MySQL database...')
    connect = MySQLConnection(**db_config)
    if connect.is_connected():
        print('Connection established.')
    else:
        print('Connection failed.')

except Error as error:
    print(error)
