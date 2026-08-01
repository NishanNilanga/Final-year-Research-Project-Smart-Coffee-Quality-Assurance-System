# ============================================================
# CoffeeSense AI
# Confidence Engine
# ============================================================



def calculate_confidence(
        moisture_status,
        color_status
):


    confidence=100



    if moisture_status=="WARN":

        confidence-=10


    elif moisture_status=="HOLD":

        confidence-=25



    if color_status=="WARN":

        confidence-=10


    elif color_status=="HOLD":

        confidence-=25



    return max(
        confidence,
        50
    )