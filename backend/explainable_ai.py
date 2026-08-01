# ============================================================
# CoffeeSense AI
# Explainable AI Decision Layer
# ============================================================


def analyze_sensor_impact(
        moisture,
        red,
        green,
        blue,
        temperature,
        humidity
):


    explanations = []

    impact = {}



    # --------------------------------------------------------
    # Moisture Analysis
    # --------------------------------------------------------

    if moisture < 350:


        impact["moisture"] = "HIGH"


        explanations.append({

            "factor":
            "Moisture",

            "level":
            "HIGH",

            "reason":
            "Moisture level is below the acceptable packing stability range.",

            "value":
            moisture

        })


    elif moisture < 430:


        impact["moisture"] = "MEDIUM"


        explanations.append({

            "factor":
            "Moisture",

            "level":
            "MEDIUM",

            "reason":
            "Moisture value requires monitoring before packing.",

            "value":
            moisture

        })


    else:


        impact["moisture"] = "LOW"





    # --------------------------------------------------------
    # Humidity Analysis
    # --------------------------------------------------------


    if humidity > 70:


        impact["humidity"] = "HIGH"


        explanations.append({

            "factor":
            "Humidity",

            "level":
            "HIGH",

            "reason":
            "High environmental humidity can increase moisture absorption.",

            "value":
            humidity

        })


    elif humidity >55:


        impact["humidity"]="MEDIUM"


        explanations.append({

            "factor":
            "Humidity",

            "level":
            "MEDIUM",

            "reason":
            "Storage humidity should be controlled.",

            "value":
            humidity

        })


    else:


        impact["humidity"]="LOW"






    # --------------------------------------------------------
    # Temperature Analysis
    # --------------------------------------------------------


    if temperature >40:


        impact["temperature"]="HIGH"


        explanations.append({

            "factor":
            "Temperature",

            "level":
            "HIGH",

            "reason":
            "High temperature exposure may affect coffee stability.",

            "value":
            temperature

        })


    else:


        impact["temperature"]="LOW"






    # --------------------------------------------------------
    # Color Analysis
    # --------------------------------------------------------


    color_variation = (

        abs(red-324)

        +

        abs(green-392)

        +

        abs(blue-329)

    )



    if color_variation >300:


        impact["color"]="HIGH"


        explanations.append({

            "factor":
            "Color",

            "level":
            "HIGH",

            "reason":
            "RGB values indicate significant roast/color variation.",

            "value":

            f"{red},{green},{blue}"

        })


    elif color_variation >150:


        impact["color"]="MEDIUM"


        explanations.append({

            "factor":
            "Color",

            "level":
            "MEDIUM",

            "reason":
            "Minor roast consistency variation detected.",

            "value":

            f"{red},{green},{blue}"

        })


    else:


        impact["color"]="LOW"





    # --------------------------------------------------------
    # Main Cause
    # --------------------------------------------------------


    highest = "No critical issue"


    if "HIGH" in impact.values():


        for key,value in impact.items():


            if value=="HIGH":

                highest=key.capitalize()

                break




    return {


        "main_cause":

        highest,


        "impact":

        impact,


        "explanations":

        explanations

    }