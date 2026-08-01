# ============================================================
# CoffeeSense AI
# Recovery Simulation Engine
# ============================================================


def simulate_moisture_recovery(
        current_moisture,
        drying_minutes=30
):


    timeline=[]


    moisture=current_moisture



    intervals = [

        0,

        5,

        10,

        15,

        20,

        25,

        30

    ]



    for minute in intervals:


        reduction = (

            minute *

            6

        )


        predicted = current_moisture + reduction



        if predicted >450:

            predicted=450



        timeline.append({

            "minute":

            minute,


            "moisture":

            predicted

        })




    final_value = timeline[-1]["moisture"]




    if final_value >=430:


        prediction="PASS"


    elif final_value>=350:


        prediction="WARN"


    else:


        prediction="HOLD"





    return {


        "initial_moisture":

        current_moisture,


        "simulation":

        timeline,


        "predicted_moisture":

        final_value,


        "predicted_status":

        prediction,


        "confidence":

        85

    }






def simulate_color_recovery(
        current_status
):


    if current_status=="HOLD":


        return {


        "action":

        "Review roasting parameters and improve colour consistency",


        "expected":

        "Improved roast uniformity after process adjustment",


        "confidence":

        75

        }



    return {


        "action":

        "No colour correction required",


        "expected":

        "Maintain current roasting condition",


        "confidence":

        95

    }