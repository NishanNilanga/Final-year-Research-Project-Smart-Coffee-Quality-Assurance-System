import serial
import time


VALID_STATUSES = {"PASS", "WARN", "HOLD"}


def is_valid_arduino_line(line):
    """
    Validate Arduino serial line.

    Expected format:
    moisture,red,green,blue,status

    Example:
    553,60,73,64,PASS
    552,76,89,76,HOLD
    """

    if not line:
        return False

    line = line.strip()

    if "," not in line:
        return False

    parts = line.split(",")

    if len(parts) != 5:
        return False

    try:
        moisture = int(parts[0].strip())
        r = int(parts[1].strip())
        g = int(parts[2].strip())
        b = int(parts[3].strip())
        status = parts[4].strip().upper()

        if status not in VALID_STATUSES:
            return False

        # Basic sensor value safety check
        if moisture < 0 or r < 0 or g < 0 or b < 0:
            return False

        return True

    except ValueError:
        return False


def read_from_arduino(port="COM3", baud_rate=9600):
    """
    Read one valid line from Arduino.

    Expected Arduino output:
    moisture,red,green,blue,status

    Example:
    553,60,73,64,PASS
    557,67,76,70,WARN
    552,76,89,76,HOLD
    """

    ser = None

    try:
        ser = serial.Serial(port, baud_rate, timeout=2)

        # Arduino resets when serial connection opens.
        # Give it time to start sending fresh readings.
        time.sleep(2.5)

        ser.reset_input_buffer()

        valid_line = ""

        # Try multiple readings because first few lines can be empty/noisy.
        for _ in range(20):
            raw_line = ser.readline().decode("utf-8", errors="ignore").strip()

            if not raw_line:
                continue

            if is_valid_arduino_line(raw_line):
                valid_line = raw_line
                break

        return valid_line

    except serial.SerialException as e:
        raise RuntimeError(
            f"Could not open Arduino port {port}. "
            f"Close Arduino Serial Monitor/test_serial.py and check COM port. Details: {e}"
        )

    finally:
        if ser is not None and ser.is_open:
            ser.close()