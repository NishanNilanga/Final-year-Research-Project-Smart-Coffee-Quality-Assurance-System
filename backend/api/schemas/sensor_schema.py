from pydantic import BaseModel



class SensorData(BaseModel):

    batch_id:str

    moisture:int

    red:int

    green:int

    blue:int

    temperature:float

    humidity:float



class QualityResponse(BaseModel):

    status:str

    score:int

    confidence:int

    recovery:str