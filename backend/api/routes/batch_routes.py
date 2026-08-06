# ============================================================
# CoffeeSense AI
# Batch Management API Routes
# ============================================================

from fastapi import APIRouter, HTTPException
from backend.database import get_connection


router = APIRouter(
    prefix="/batch",
    tags=["Batch Management"]
)



# ============================================================
# Create Batch
# ============================================================

@router.post("/create")
def create_batch(batch_id: str):

    return {

        "message": "Batch created successfully",

        "data": {

            "batch_id": batch_id,

            "status": "CREATED"

        }

    }





# ============================================================
# Get All Batch History
# ============================================================

@router.get("/history")
def get_batch_history():


    connection = get_connection()

    cursor = connection.cursor()


    try:

        cursor.execute(
            """
            SELECT *
            FROM quality_records
            ORDER BY id DESC
            """
        )


        records = cursor.fetchall()



        columns = [

            "id",

            "batch_id",

            "timestamp",

            "moisture",

            "red",

            "green",

            "blue",

            "temperature",

            "humidity",

            "status",

            "quality_score",

            "confidence",

            "recommendation"

        ]



        history = []


        for row in records:


            history.append(

                dict(zip(columns,row))

            )



        return {


            "count": len(history),


            "batches": history


        }



    finally:


        connection.close()





# ============================================================
# Get Single Batch Details
# ============================================================

@router.get("/{batch_id}")
def get_single_batch(batch_id: str):


    connection = get_connection()

    cursor = connection.cursor()



    try:


        cursor.execute(

            """

            SELECT *

            FROM quality_records

            WHERE batch_id=?

            ORDER BY id DESC

            """,

            (batch_id,)

        )


        records = cursor.fetchall()



        if not records:

            raise HTTPException(

                status_code=404,

                detail="Batch not found"

            )



        columns = [

            "id",

            "batch_id",

            "timestamp",

            "moisture",

            "red",

            "green",

            "blue",

            "temperature",

            "humidity",

            "status",

            "quality_score",

            "confidence",

            "recommendation"

        ]



        batches = []


        for row in records:


            batches.append(

                dict(zip(columns,row))

            )



        return {


            "batch_id": batch_id,


            "records": batches


        }



    finally:

        connection.close()