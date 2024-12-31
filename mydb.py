import mysql.connector

dataBase = mysql.connector.connect(
    host = '127.0.0.1',
    user = 'root',
    passwd = 'I_love_bingo1',
)

cursorObject = dataBase.cursor()

cursorObject.execute("CREATE DATABASE Lovato_Test")