# ============================================================
# CoffeeSense AI
# Recovery Intelligence Engine
# ============================================================


from backend.models import RecoveryPlan




def generate_recovery_plan(
        quality_result,
        temperature,
        humidity
):


    actions=[]

    problems=[]


    severity="LOW"




    if quality_result.moisture_status=="HOLD":


        problems.append(
            "High moisture instability"
        )


        severity="HIGH"



        actions.extend(

        [

        "Start controlled drying process",

        "Maintain drying temperature between 40-45°C",

        "Reduce environmental humidity below 55%",

        "Re-test moisture level after drying"

        ]

        )





    elif quality_result.moisture_status=="WARN":


        problems.append(
            "Moisture slightly outside optimal range"
        )


        actions.append(

            "Perform additional drying adjustment"

        )





    if quality_result.color_status=="HOLD":


        problems.append(

            "Coffee roast colour deviation detected"

        )


        severity="HIGH"



        actions.extend(

        [

        "Check roasting temperature",

        "Verify roasting duration",

        "Inspect batch mixing consistency"

        ]

        )





    if humidity >70:


        actions.append(

            "Control storage humidity environment"

        )





    if temperature >40:


        actions.append(

            "Reduce temperature exposure"

        )





    if len(problems)==0:


        return RecoveryPlan(

            problem="No issues detected",

            severity="LOW",

            actions=[

            "Coffee powder ready for packing"

            ],

            expected_result=

            "Maintain current conditions",

            recovery_probability=95

        )





    return RecoveryPlan(

        problem=" + ".join(problems),

        severity=severity,

        actions=actions,

        expected_result=

        "Quality parameters expected to improve after recovery process",

        recovery_probability=85

    )