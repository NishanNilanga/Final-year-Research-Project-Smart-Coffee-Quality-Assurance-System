# ============================================================
# CoffeeSense AI
# Backend Intelligence Testing
# ============================================================


from backend.models import SensorReading


from backend.quality_engine import (
    run_quality_analysis
)


from backend.recovery_engine import (
    generate_recovery_plan
)


from backend.confidence_engine import (
    calculate_confidence
)


from backend.recommendation_engine import (
    format_recommendation
)



# ============================================================
# TEST FUNCTION
# ============================================================


def run_test(title, sensor):


    print("\n")
    print("=" * 60)

    print(title)

    print("=" * 60)



    print("\nINPUT SENSOR DATA")

    print("------------------")

    print(
        f"Moisture : {sensor.moisture}"
    )

    print(
        f"RGB      : {sensor.red}, {sensor.green}, {sensor.blue}"
    )

    print(
        f"Temperature : {sensor.temperature} C"
    )

    print(
        f"Humidity : {sensor.humidity} %"
    )



    # Quality analysis

    result = run_quality_analysis(
        sensor
    )



    confidence = calculate_confidence(

        result.moisture_status,

        result.color_status

    )


    result.confidence = confidence



    print("\nQUALITY RESULT")

    print("------------------")


    print(
        "Status:",
        result.status
    )


    print(
        "Quality Score:",
        result.quality_score
    )


    print(
        "Confidence:",
        result.confidence
    )


    print(
        "Issues:",
        result.issues
    )




    # Recovery analysis


    recovery = generate_recovery_plan(

        result,

        sensor.temperature,

        sensor.humidity

    )



    recommendation = format_recommendation(

        recovery

    )



    print("\nRECOVERY INTELLIGENCE")

    print("------------------")


    print(
        "Problem:"
    )

    print(
        recommendation["problem"]
    )


    print(
        "\nSeverity:"
    )

    print(
        recommendation["severity"]
    )



    print(
        "\nRecommended Actions:"
    )


    for action in recommendation["actions"]:

        print(
            " -",
            action
        )



    print(
        "\nExpected Result:"
    )

    print(
        recommendation["expected"]
    )



    print(
        "\nRecovery Probability:"
    )

    print(
        recommendation["probability"],
        "%"
    )



# ============================================================
# TEST CASE 1
# GOOD COFFEE SAMPLE
# ============================================================


pass_sample = SensorReading(

    moisture=520,

    red=320,

    green=390,

    blue=330,

    temperature=32,

    humidity=50

)



run_test(

    "TEST 1 : GOOD COFFEE POWDER",

    pass_sample

)





# ============================================================
# TEST CASE 2
# BAD COFFEE SAMPLE
# ============================================================


hold_sample = SensorReading(

    moisture=250,

    red=500,

    green=600,

    blue=520,

    temperature=42,

    humidity=80

)



run_test(

    "TEST 2 : LOW QUALITY COFFEE POWDER",

    hold_sample

)