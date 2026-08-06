# ============================================================
# CoffeeSense AI
# PDF Report Generation API Routes
# ============================================================

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend.database import get_connection
from backend.services.pdf_report_service import generate_pdf_report


router = APIRouter(
    prefix="/report",
    tags=["Reports"]
)



# ============================================================
# Health Check
# ============================================================

@router.get("/health")
def report_health():

    return {
        "status": "Report service running"
    }



# ============================================================
# Generate JSON Report
# ============================================================

@router.get("/generate/{batch_id}")
def generate_report(batch_id: str):

    connection = get_connection()
    cursor = connection.cursor()


    try:

        cursor.execute(
            """
            SELECT *
            FROM quality_records
            WHERE batch_id=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (batch_id,)
        )


        record = cursor.fetchone()


        if not record:

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


        batch = dict(zip(columns, record))


        return {

            "report_title":
            "CoffeeSense AI Quality Report",


            "batch_information":{

                "batch_id": batch["batch_id"],
                "tested_time": batch["timestamp"]

            },


            "sensor_data":{

                "moisture": batch["moisture"],

                "color":{

                    "red":batch["red"],
                    "green":batch["green"],
                    "blue":batch["blue"]

                },

                "temperature":batch["temperature"],
                "humidity":batch["humidity"]

            },


            "quality_analysis":{

                "status":batch["status"],
                "quality_score":batch["quality_score"],
                "confidence":batch["confidence"]

            },


            "recovery_recommendation":
            batch["recommendation"],


            "final_decision":

            (
                "Ready for packing"
                if batch["status"]=="PASS"
                else
                "Recovery process required"
            )

        }


    finally:

        connection.close()




# ============================================================
# Generate PDF Report
# ============================================================

@router.get("/pdf/{batch_id}")
def generate_pdf(batch_id:str):


    connection = get_connection()

    cursor = connection.cursor()


    try:


        cursor.execute(

            """
            SELECT *
            FROM quality_records
            WHERE batch_id=?
            ORDER BY id DESC
            LIMIT 1
            """,

            (batch_id,)

        )


        record = cursor.fetchone()


        if not record:


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



        batch = dict(zip(columns,record))



        pdf_path = generate_pdf_report(batch)



        return FileResponse(

            path=pdf_path,

            media_type="application/pdf",

            filename=
            f"CoffeeSense_Report_{batch_id}.pdf"

        )


    finally:

        connection.close()