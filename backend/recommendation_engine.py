# ============================================================
# CoffeeSense AI
# Recommendation Formatter
# ============================================================



def format_recommendation(
        recovery_plan
):


    return {


    "problem":

    recovery_plan.problem,



    "severity":

    recovery_plan.severity,



    "actions":

    recovery_plan.actions,



    "expected":

    recovery_plan.expected_result,



    "probability":

    recovery_plan.recovery_probability


    }