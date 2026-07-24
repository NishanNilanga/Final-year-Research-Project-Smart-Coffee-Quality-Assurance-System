# ============================================================
# Coffee Powder Packing Readiness Decision Logic
# ============================================================
# Arduino serial format:
# moisture,red,green,blue,status
#
# Example:
# 552,320,382,328,PASS
# 330,399,454,376,HOLD
#
# Note:
# TCS3200 values are sensor frequency/pulse readings.
# These are NOT normal camera RGB 0-255 color values.
# TCS3200 readings depend on chamber light, sensor distance,
# sample height, and sensor angle.
# ============================================================


# ============================================================
# COLOR REFERENCE VALUES
# ============================================================
# Final chamber accepted / correct coffee powder readings:
# R approximately 271 - 422
# G approximately 355 - 475
# B approximately 305 - 355
#
# Accepted reference average selected:
# R = 324, G = 392, B = 329
#
# Distance logic:
# PASS = close to accepted normal coffee powder
# WARN = slight roast/color variation
# HOLD = large/rejected color variation
# ============================================================

REFERENCE_R = 324
REFERENCE_G = 392
REFERENCE_B = 329

COLOR_PASS_DISTANCE = 145
COLOR_WARN_DISTANCE = 190


# ============================================================
# MOISTURE THRESHOLDS
# ============================================================
# Higher value = dry/stable
# Lower value  = wet/risky
#
# PASS = moisture_raw >= 430
# WARN = 350 <= moisture_raw < 430
# HOLD = moisture_raw < 350
# ============================================================

MOISTURE_PASS_LIMIT = 430
MOISTURE_WARN_LIMIT = 350


def color_distance(r, g, b, ref_r=REFERENCE_R, ref_g=REFERENCE_G, ref_b=REFERENCE_B):
    """
    Calculate distance between current TCS3200 reading and accepted reference color.

    Smaller distance = closer to normal accepted coffee powder color.
    Larger distance  = rejected / inconsistent roast color variation.
    """

    return ((r - ref_r) ** 2 + (g - ref_g) ** 2 + (b - ref_b) ** 2) ** 0.5


def classify_moisture(moisture_raw):
    """
    Classify moisture status using calibrated threshold values.
    """

    if moisture_raw >= MOISTURE_PASS_LIMIT:
        return "PASS"

    if MOISTURE_WARN_LIMIT <= moisture_raw < MOISTURE_PASS_LIMIT:
        return "WARN"

    return "HOLD"


def classify_color(r, g, b):
    """
    Classify roast/color consistency using TCS3200 color distance.

    Correct/accepted powder example:
    Around R=324, G=392, B=329 -> PASS

    Slight variation:
    Distance between 146 and 190 -> WARN

    Rejected/large color variation:
    Distance above 190 -> HOLD
    """

    distance = color_distance(r, g, b)

    if distance <= COLOR_PASS_DISTANCE:
        return "PASS"

    if distance <= COLOR_WARN_DISTANCE:
        return "WARN"

    return "HOLD"


def combine_status(moisture_status, color_status):
    """
    Final decision uses worst-case logic.

    If moisture OR color is HOLD -> final HOLD
    Else if moisture OR color is WARN -> final WARN
    Else final PASS
    """

    if moisture_status == "HOLD" or color_status == "HOLD":
        return "HOLD"

    if moisture_status == "WARN" or color_status == "WARN":
        return "WARN"

    return "PASS"


def calculate_readiness_score(moisture_status, color_status):
    """
    Calculate readiness score for dashboard visualization.
    """

    score = 100

    if moisture_status == "WARN":
        score -= 25
    elif moisture_status == "HOLD":
        score -= 50

    if color_status == "WARN":
        score -= 20
    elif color_status == "HOLD":
        score -= 40

    return max(score, 0)


def parse_arduino_line(line):
    """
    Parse Arduino serial output.

    Expected Arduino output:
    moisture,red,green,blue,status

    Example:
    552,320,382,328,PASS
    330,399,454,376,HOLD

    Returns:
    moisture, r, g, b, arduino_status
    """

    if not line:
        return None

    line = line.strip()

    # Ignore debug lines or invalid serial noise
    if "," not in line:
        return None

    parts = line.split(",")

    if len(parts) < 5:
        return None

    try:
        moisture = int(parts[0].strip())
        r = int(parts[1].strip())
        g = int(parts[2].strip())
        b = int(parts[3].strip())
        arduino_status = parts[4].strip().upper()

        if arduino_status not in ["PASS", "WARN", "HOLD"]:
            return None

        return moisture, r, g, b, arduino_status

    except ValueError:
        return None