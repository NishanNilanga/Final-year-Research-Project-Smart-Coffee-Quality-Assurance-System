# ============================================================
# Coffee Powder Packing Readiness Decision Logic
# Industry Upgrade Version
#
# Arduino Serial Format:
#
# moisture,r,g,b,temperature,humidity,status
#
# Example:
# 500,409,582,474,34.4,35.7,PASS
#
# ============================================================



# ============================================================
# FINAL COLOR CALIBRATION
#
# Based on real device testing
#
# GOOD COFFEE SAMPLE:
# R = 386
# G = 618
# B = 462
#
# ============================================================


REFERENCE_R = 386
REFERENCE_G = 618
REFERENCE_B = 462



COLOR_PASS_DISTANCE = 120
COLOR_WARN_DISTANCE = 200



# ============================================================
# MOISTURE CALIBRATION
#
# GOOD:
# ~500
#
# BAD:
# ~240
#
# ============================================================


MOISTURE_PASS_LIMIT = 430
MOISTURE_WARN_LIMIT = 300



# ============================================================
# COLOR DISTANCE
# ============================================================

def color_distance(r,g,b):

    return (
        (r-REFERENCE_R)**2 +
        (g-REFERENCE_G)**2 +
        (b-REFERENCE_B)**2
    ) ** 0.5



# ============================================================
# MOISTURE CLASSIFICATION
# ============================================================

def classify_moisture(moisture):

    if moisture >= MOISTURE_PASS_LIMIT:
        return "PASS"


    elif moisture >= MOISTURE_WARN_LIMIT:
        return "WARN"


    else:
        return "HOLD"



# ============================================================
# COLOR CLASSIFICATION
# ============================================================

def classify_color(r,g,b):

    distance = color_distance(r,g,b)


    if distance <= COLOR_PASS_DISTANCE:
        return "PASS"


    elif distance <= COLOR_WARN_DISTANCE:
        return "WARN"


    else:
        return "HOLD"




# ============================================================
# FINAL QUALITY DECISION
# ============================================================

def combine_status(moisture_status,color_status):


    if moisture_status == "HOLD" or color_status == "HOLD":
        return "HOLD"



    if moisture_status == "WARN" or color_status == "WARN":
        return "WARN"



    return "PASS"




# ============================================================
# RECOVERY RECOMMENDATION
# Panel Comment Solution
# ============================================================

def generate_recommendation(
        moisture_status,
        color_status,
        temperature,
        humidity
):


    problems = []
    recommendations = []



    if moisture_status == "HOLD":

        problems.append(
            "High moisture variation detected"
        )

        recommendations.append(
            "Increase drying duration before packing"
        )



    elif moisture_status == "WARN":

        problems.append(
            "Moisture level requires attention"
        )

        recommendations.append(
            "Perform additional drying inspection"
        )



    if color_status == "HOLD":

        problems.append(
            "Coffee color inconsistency detected"
        )

        recommendations.append(
            "Check roasting temperature and roasting time"
        )



    elif color_status == "WARN":

        problems.append(
            "Slight roast color variation detected"
        )

        recommendations.append(
            "Review roasting parameters"
        )



    if humidity > 75:

        recommendations.append(
            "Control storage humidity conditions"
        )



    if len(problems)==0:

        return {
            "issue":"No quality issues detected",
            "recommendation":"Ready for packing"
        }



    return {

        "issue":" + ".join(problems),

        "recommendation":
            " + ".join(recommendations)

    }




# ============================================================
# CONFIDENCE SCORE
# ============================================================

def calculate_confidence(
        moisture_status,
        color_status
):


    if moisture_status=="PASS" and color_status=="PASS":
        return 95



    if moisture_status=="WARN" or color_status=="WARN":
        return 70



    return 35





# ============================================================
# READINESS SCORE
# ============================================================

def calculate_readiness_score(
        moisture_status,
        color_status
):


    score = 100



    if moisture_status=="WARN":
        score -= 20

    elif moisture_status=="HOLD":
        score -= 50



    if color_status=="WARN":
        score -= 20

    elif color_status=="HOLD":
        score -= 40



    return max(score,0)





# ============================================================
# SERIAL DATA PARSER
# ============================================================

def parse_arduino_line(line):


    if not line:
        return None



    if "," not in line:
        return None



    parts = line.strip().split(",")



    if len(parts) < 7:
        return None



    try:

        moisture = int(parts[0])

        r = int(parts[1])

        g = int(parts[2])

        b = int(parts[3])


        temperature = float(parts[4])

        humidity = float(parts[5])


        status = parts[6].upper()



        return {

            "moisture":moisture,

            "red":r,

            "green":g,

            "blue":b,

            "temperature":temperature,

            "humidity":humidity,

            "arduino_status":status

        }



    except:

        return None