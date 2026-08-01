# ============================================================
# CoffeeSense AI
# Database Models
# ============================================================


from dataclasses import dataclass



@dataclass
class QualityRecord:


    batch_id:str


    timestamp:str


    moisture:int


    red:int


    green:int


    blue:int


    temperature:float


    humidity:float


    status:str


    quality_score:int


    confidence:int


    recommendation:str