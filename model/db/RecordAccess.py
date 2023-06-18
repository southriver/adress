import mysql.connector

from model.config import Config

class RecordAccess:

    def __init_(self):
        pass
    
    def getConnection(self):

        host = Config.MYSQL_HOST
        port = Config.MYSQL_PORT
        username = Config.MYSQL_USERNAME
        password = Config.MYSQL_PASSWORD
        database = Config.MYSQL_DATABASE

        configLocal = {
        'user': username,
        'password': password,
        'host': host,
        'database': database,
        'raise_on_warnings': True
        }

        cnx = mysql.connector.connect(**configLocal)

        return cnx

    def insert(self, sql, data):
        mydb = None
        cursor = None
        try:
            mydb = self.getConnection()
            cursor = mydb.cursor()

            cursor.execute(sql, data)
            id = cursor.lastrowid
            
            mydb.commit()

            return id
        
        except Exception as error:
            if mydb:
                mydb.rollback()
            raise

        finally:
            # Close the cursor and database connection
            if cursor:
                cursor.close()
            if mydb:
                mydb.close()

    def update(self, sql, data,Id):
        mydb = None
        cursor = None
        try:
            mydb = self.getConnection()
            cursor = mydb.cursor()

            cursor.execute(sql, data)
            affectedCnt = cursor.rowcount

            mydb.commit()

            return affectedCnt
        
        except Exception as error:
            if mydb:
                mydb.rollback()
            raise

        finally:
            # Close the cursor and database connection
            if cursor:
                cursor.close()
            if mydb:
                mydb.close()

    def query(self, query, data):
        mydb = None
        cursor = None
        result = []
        
        try:
            mydb = self.getConnection()
            cursor = mydb.cursor()

            cursor.execute(query, data)

            # Fetch all rows from the result set
            result = cursor.fetchall()
            return result
        
        except Exception as error:
            if mydb:
                mydb.rollback()
            raise

        finally:
            # Close the cursor and database connection
            if cursor:
                cursor.close()
            if mydb:
                mydb.close()