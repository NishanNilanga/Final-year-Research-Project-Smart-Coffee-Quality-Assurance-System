# ============================================================
# CoffeeSense AI
# Database Service Layer
# FastAPI <-> SQLite Connection
# ============================================================


from datetime import datetime

from backend.database import (
    get_connection
)



def save_sensor_data(sensor, quality_result, recommendation=""):

    """
    Save analyzed sensor reading
    into SQLite database
    """

    connection = get_connection()

    cursor = connection.cursor()



    cursor.execute(

        """
        INSERT INTO quality_records
        (
            batch_id,
            timestamp,
            moisture,
            red,
            green,
            blue,
            temperature,
            humidity,
            status,
            quality_score,
            confidence,
            recommendation
        )

        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )

        """,

        (

            sensor.batch_id,

            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

            sensor.moisture,

            sensor.red,

            sensor.green,

            sensor.blue,

            sensor.temperature,

            sensor.humidity,

            quality_result.status,

            quality_result.quality_score,

            quality_result.confidence,

            recommendation

        )

    )


    connection.commit()

    record_id = cursor.lastrowid

    connection.close()



    return {

        "record_id":record_id,

        "saved":True

    }





def fetch_sensor_history(limit=50):

    """
    Retrieve previous quality records
    """


    connection = get_connection()

    cursor = connection.cursor()



    cursor.execute(

        """
        SELECT *
        FROM quality_records
        ORDER BY id DESC
        LIMIT ?

        """,

        (limit,)

    )


    rows = cursor.fetchall()


    connection.close()



    records=[]


    for row in rows:

        records.append(

            {

                "id":row[0],

                "batch_id":row[1],

                "timestamp":row[2],

                "moisture":row[3],

                "red":row[4],

                "green":row[5],

                "blue":row[6],

                "temperature":row[7],

                "humidity":row[8],

                "status":row[9],

                "quality_score":row[10],

                "confidence":row[11],

                "recommendation":row[12]

            }

        )


    return records