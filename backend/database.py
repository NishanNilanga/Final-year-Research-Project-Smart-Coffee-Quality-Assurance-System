# ============================================================
# CoffeeSense AI
# SQLite Database Manager
# ============================================================


import sqlite3
import os



DATABASE_PATH = os.path.join(

    os.path.dirname(
        os.path.dirname(__file__)
    ),

    "data",

    "coffee_quality.db"

)




def get_connection():


    os.makedirs(

        os.path.dirname(DATABASE_PATH),

        exist_ok=True

    )


    return sqlite3.connect(
        DATABASE_PATH
    )





def initialize_database():


    connection = get_connection()


    cursor = connection.cursor()



    cursor.execute(

    """

    CREATE TABLE IF NOT EXISTS quality_records
    (

        id INTEGER PRIMARY KEY AUTOINCREMENT,


        batch_id TEXT,


        timestamp TEXT,


        moisture INTEGER,


        red INTEGER,


        green INTEGER,


        blue INTEGER,


        temperature REAL,


        humidity REAL,


        status TEXT,


        quality_score INTEGER,


        confidence INTEGER,


        recommendation TEXT

    )

    """

    )


    connection.commit()


    connection.close()