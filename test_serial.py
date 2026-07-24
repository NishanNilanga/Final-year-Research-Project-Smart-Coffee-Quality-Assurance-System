import serial
import time

from backend.logic import (
    parse_arduino_line,
    classify_moisture,
    classify_color,
    combine_status,
    calculate_readiness_score,
    color_distance,
)

PORT = "COM3"
BAUD_RATE = 9600


def main():
    ser = None

    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=2)
        time.sleep(2.5)

        print("✅ Connected to Arduino")
        print("Reading serial data...")
        print("Expected format: moisture,red,green,blue,status")
        print("-" * 90)

        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()

            if not line:
                continue

            parsed = parse_arduino_line(line)

            if parsed is None:
                print(f"⚠️ Ignored invalid/noisy line: {line}")
                continue

            moisture, r, g, b, arduino_status = parsed

            moisture_status = classify_moisture(moisture)
            color_status = classify_color(r, g, b)
            final_status = combine_status(moisture_status, color_status)
            readiness_score = calculate_readiness_score(moisture_status, color_status)
            distance = color_distance(r, g, b)

            print(f"Raw Arduino Line      : {line}")
            print(f"Moisture Raw          : {moisture}")
            print(f"Color Values          : R={r}, G={g}, B={b}")
            print(f"Color Distance        : {distance:.2f}")
            print(f"Arduino Final Status  : {arduino_status}")
            print(f"Moisture Status       : {moisture_status}")
            print(f"Color Status          : {color_status}")
            print(f"Dashboard Final Status: {final_status}")
            print(f"Readiness Score       : {readiness_score}%")

            if final_status == "PASS":
                print("✅ Factory Action      : Ready for packing")
            elif final_status == "WARN":
                print("⚠️ Factory Action      : Monitor / recheck before packing")
            else:
                print("🚫 Factory Action      : HOLD - do not pack")

            print("-" * 90)

    except serial.SerialException as e:
        print("❌ Serial connection error:")
        print(e)
        print("\nFix:")
        print("1. Check Arduino COM port.")
        print("2. Close Arduino Serial Monitor.")
        print("3. Close Streamlit dashboard if it is using COM3.")
        print("4. Make sure Arduino is connected by USB.")

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        if ser is not None and ser.is_open:
            ser.close()


if __name__ == "__main__":
    main()