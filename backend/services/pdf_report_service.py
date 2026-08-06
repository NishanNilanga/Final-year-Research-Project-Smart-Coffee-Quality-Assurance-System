# ============================================================
# CoffeeSense AI
# PDF Report Generator Service
# ============================================================


import os

from reportlab.lib.pagesizes import A4

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet



# Create reports folder

REPORT_FOLDER = "reports"

os.makedirs(
    REPORT_FOLDER,
    exist_ok=True
)



def generate_pdf_report(batch):


    file_name = (
        f"CoffeeSense_Report_{batch['batch_id']}.pdf"
    )


    file_path = os.path.join(
        REPORT_FOLDER,
        file_name
    )



    pdf = SimpleDocTemplate(

        file_path,

        pagesize=A4

    )


    styles = getSampleStyleSheet()


    content = []



    # Title

    content.append(

        Paragraph(

            "CoffeeSense AI Quality Report",

            styles["Title"]

        )

    )


    content.append(

        Spacer(1,20)

    )



    # Batch Information

    data = [


        [
            "Batch ID",
            batch["batch_id"]
        ],


        [
            "Tested Time",
            batch["timestamp"]
        ],


        [
            "Quality Status",
            batch["status"]
        ],


        [
            "Quality Score",
            str(batch["quality_score"])
        ],


        [
            "Confidence",
            str(batch["confidence"])
        ],


        [
            "Moisture Level",
            str(batch["moisture"])
        ],


        [
            "Temperature",
            str(batch["temperature"])+" °C"
        ],


        [
            "Humidity",
            str(batch["humidity"])+" %"
        ],



        [
            "RGB Values",

            f"R:{batch['red']} "
            f"G:{batch['green']} "
            f"B:{batch['blue']}"
        ],



        [
            "Recommendation",

            batch["recommendation"]

        ]

    ]



    table = Table(

        data,

        colWidths=[120,300]

    )



    table.setStyle(

        TableStyle(

            [

                (
                "GRID",
                (0,0),
                (-1,-1),
                1,
                None
                ),


                (
                "VALIGN",
                (0,0),
                (-1,-1),
                "TOP"
                )

            ]

        )

    )



    content.append(table)



    content.append(

        Spacer(1,25)

    )



    # Final Decision


    if batch["status"] == "PASS":

        decision = "READY FOR PACKING"

    else:

        decision = "RECOVERY PROCESS REQUIRED"



    content.append(

        Paragraph(

            "Final Decision : "
            + decision,

            styles["Heading2"]

        )

    )



    pdf.build(content)



    return file_path