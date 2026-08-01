# ============================================================
# CoffeeSense AI
# Sensor Data Logger
# ============================================================


from backend.database import get_connection



def save_quality_record(data):


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


    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)

    """,

    (

    data["batch_id"],

    data["timestamp"],

    data["moisture"],

    data["red"],

    data["green"],

    data["blue"],

    data["temperature"],

    data["humidity"],

    data["status"],

    data["quality_score"],

    data["confidence"],

    data["recommendation"]

    )

    )


    connection.commit()


    connection.close()