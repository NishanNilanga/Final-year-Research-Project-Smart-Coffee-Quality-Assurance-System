# ============================================================
# CoffeeSense AI
# Quality Intelligence Engine
# ============================================================


from backend.models import (
    SensorReading,
    QualityResult
)



REFERENCE_R = 324
REFERENCE_G = 392
REFERENCE_B = 329



def calculate_color_distance(
        r,
        g,
        b
):


    return (

        (

            (r-REFERENCE_R)**2 +

            (g-REFERENCE_G)**2 +

            (b-REFERENCE_B)**2

        )

    ) ** 0.5





def analyze_moisture(
        moisture
):


    if moisture >= 430:

        return "PASS"


    elif moisture >=350:

        return "WARN"


    else:

        return "HOLD"





def analyze_color(
        r,
        g,
        b
):


    distance = calculate_color_distance(
        r,
        g,
        b
    )


    if distance <=145:

        return "PASS"



    elif distance <=190:

        return "WARN"



    else:

        return "HOLD"





def calculate_score(
        moisture_status,
        color_status
):


    score=100



    if moisture_status=="WARN":

        score-=20


    elif moisture_status=="HOLD":

        score-=45



    if color_status=="WARN":

        score-=15


    elif color_status=="HOLD":

        score-=35



    return max(score,0)





def run_quality_analysis(
        sensor:SensorReading
):


    moisture_status = analyze_moisture(
        sensor.moisture
    )


    color_status = analyze_color(

        sensor.red,

        sensor.green,

        sensor.blue

    )



    if (

        moisture_status=="HOLD"

        or

        color_status=="HOLD"

    ):

        final="HOLD"



    elif (

        moisture_status=="WARN"

        or

        color_status=="WARN"

    ):

        final="WARN"



    else:

        final="PASS"





    issues=[]


    if moisture_status!="PASS":

        issues.append(
            "Moisture instability detected"
        )


    if color_status!="PASS":

        issues.append(
            "Coffee color inconsistency detected"
        )




    return QualityResult(

        status=final,

        quality_score=calculate_score(

            moisture_status,

            color_status

        ),

        confidence=0,

        moisture_status=moisture_status,

        color_status=color_status,

        issues=issues

    )