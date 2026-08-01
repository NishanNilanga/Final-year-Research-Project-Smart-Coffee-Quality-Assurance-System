# ============================================================
# CoffeeSense AI
# Quality Report Generator
# ============================================================


from datetime import datetime



def generate_report(record):


    report=f"""


=====================================

        CoffeeSense AI

 Quality Inspection Report

=====================================


Batch ID:

{record["batch_id"]}



Inspection Time:

{record["timestamp"]}



QUALITY RESULT

-------------------------------------

Status:

{record["status"]}


Quality Score:

{record["quality_score"]}%



AI Confidence:

{record["confidence"]}%



SENSOR VALUES

-------------------------------------


Moisture:

{record["moisture"]}



RGB:

{record["red"]},

{record["green"]},

{record["blue"]}



Temperature:

{record["temperature"]}



Humidity:

{record["humidity"]}



RECOMMENDATION

-------------------------------------


{record["recommendation"]}



Generated:

{datetime.now()}


=====================================

"""


    return report