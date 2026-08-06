from fastapi import APIRouter

from backend.api.schemas.sensor_schema import SensorData

from backend.api.services.quality_service import process_quality

from backend.api.services.recovery_service import get_recovery

from backend.api.services.database_service import save_sensor_data



router = APIRouter(

    prefix="/sensor",

    tags=["Sensor"]

)



@router.post("/analyse")
def analyze_sensor(data: SensorData):


    # ===============================
    # Quality Analysis
    # ===============================

    quality_result = process_quality(data)



    # ===============================
    # Recovery Recommendation
    # ===============================

    recovery = get_recovery(
        quality_result,
        
        data.temperature,

        data.humidity
    )



    # ===============================
    # Save Database
    # ===============================

    save_sensor_data(

        data,

        quality_result,

        " | ".join(recovery.actions)

    )



    return {


        "sensor": data,


        "quality": quality_result,


        "recovery": recovery,


        "database":

        {

            "saved": True

        }


    }