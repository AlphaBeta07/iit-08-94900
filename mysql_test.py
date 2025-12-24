import mysql.connector

host = "localhost"
user = "root"
password = "manager"
database = "test_db"

try:
    connection = mysql.connector.connect(
        host = host,
        user = user,
        password = password,
        database = database
    )
    print("Connected to mysql")

    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Table in databse : ",tables)

    cursor.execute("SELECT * FROM sample_table")
    rows = cursor.fetchall()
    for row in rows:
        print(row)

    cursor.close()
    connection.close()
    print("connection closed")
except mysql.connector.Error as err:
    print("Error : ", err)