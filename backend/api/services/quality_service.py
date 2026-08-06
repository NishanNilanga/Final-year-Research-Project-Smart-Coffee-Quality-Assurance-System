# ============================================================
# CoffeeSense AI
# Quality Service
# ============================================================


from backend.models import SensorReading

from backend.quality_engine import run_quality_analysis



def process_quality(data):


    sensor = SensorReading(

        moisture=data.moisture,

        red=data.red,

        green=data.green,

        blue=data.blue,

        temperature=data.temperature,

        humidity=data.humidity

    )


    result = run_quality_analysis(
        sensor
    )


    return result