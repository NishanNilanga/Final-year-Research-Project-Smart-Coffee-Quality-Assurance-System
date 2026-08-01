# ============================================================
# CoffeeSense AI
# Batch Management
# ============================================================


from backend.database import get_connection



def get_batch_history(batch_id):


    connection=get_connection()


    cursor=connection.cursor()



    cursor.execute(

    """

    SELECT *

    FROM quality_records

    WHERE batch_id=?

    ORDER BY id DESC

    """,

    (

    batch_id,

    )

    )



    data=cursor.fetchall()


    connection.close()


    return data





def get_all_batches():


    connection=get_connection()


    cursor=connection.cursor()



    cursor.execute(

    """

    SELECT DISTINCT batch_id

    FROM quality_records

    """

    )


    batches=cursor.fetchall()


    connection.close()


    return batches