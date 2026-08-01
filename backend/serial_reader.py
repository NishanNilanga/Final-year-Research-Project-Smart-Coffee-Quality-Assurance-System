import serial
import time


VALID_STATUSES = {
    "PASS",
    "WARN",
    "HOLD"
}



# ============================================================
# Validate Arduino Data
#
# New Arduino Format:
#
# moisture,r,g,b,temp,humidity,status
#
# Example:
#
# 500,409,582,474,34.4,35.7,PASS
#
# ============================================================


def is_valid_arduino_line(line):


    if not line:
        return False



    line = line.strip()



    if "," not in line:
        return False



    parts = line.split(",")



    # Need 7 values
    if len(parts) != 7:
        return False



    try:

        moisture = int(parts[0].strip())

        r = int(parts[1].strip())

        g = int(parts[2].strip())

        b = int(parts[3].strip())


        temperature = float(parts[4].strip())

        humidity = float(parts[5].strip())


        status = parts[6].strip().upper()



        if status not in VALID_STATUSES:
            return False



        # Sensor safety validation

        if moisture < 0:
            return False


        if r < 0 or g < 0 or b < 0:
            return False



        if temperature < -10 or temperature > 100:
            return False



        if humidity < 0 or humidity > 100:
            return False



        return True



    except ValueError:

        return False





# ============================================================
# Read Arduino Serial Data
#
# Returns:
#
# Valid complete sensor reading
#
# ============================================================


def read_from_arduino(
        port="COM3",
        baud_rate=9600
):


    ser = None



    try:


        ser = serial.Serial(
            port,
            baud_rate,
            timeout=2
        )



        # Arduino reset delay

        time.sleep(2.5)



        ser.reset_input_buffer()



        valid_line = ""



        # Ignore startup noise

        for _ in range(30):


            raw_line = (
                ser.readline()
                .decode(
                    "utf-8",
                    errors="ignore"
                )
                .strip()
            )



            if not raw_line:
                continue



            if is_valid_arduino_line(raw_line):

                valid_line = raw_line

                break



        return valid_line





    except serial.SerialException as e:


        raise RuntimeError(

            f"Cannot connect Arduino on {port}. "
            f"Close Arduino Serial Monitor and check COM port. "
            f"Details: {e}"

        )





    finally:


        if ser is not None and ser.is_open:

            ser.close()