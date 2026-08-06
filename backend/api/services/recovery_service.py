# ============================================================
# CoffeeSense AI
# Recovery Recommendation Service
# ============================================================


from backend.recovery_engine import generate_recovery_plan



def get_recovery(
        result,
        temperature,
        humidity
):


    recovery = generate_recovery_plan(

        result,

        temperature,

        humidity

    )


    return recovery