# ============================================================
# CoffeeSense AI
# Data Models
# ============================================================


from dataclasses import dataclass
from typing import List



@dataclass
class SensorReading:

    moisture: int

    red: int

    green: int

    blue: int

    temperature: float

    humidity: float



@dataclass
class QualityResult:

    status: str

    quality_score: int

    confidence: int

    moisture_status: str

    color_status: str

    issues: List[str]



@dataclass
class RecoveryPlan:

    problem: str

    severity: str

    actions: List[str]

    expected_result: str

    recovery_probability: int