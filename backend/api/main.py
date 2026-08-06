from fastapi import FastAPI

from backend.api.routes import sensor_routes
from backend.api.routes import batch_routes
from backend.api.routes import report_routes
from backend.database import initialize_database




app = FastAPI(

    title="Coffee AI Analyzer API",

    description="""

    Industrial Coffee Powder Quality Analysis API

    Features:

    - Arduino Sensor Integration
    - AI Quality Decision
    - Recovery Recommendation
    - Batch History
    - Reports

    """,

    version="1.0.0"

)

initialize_database()



# Routes

app.include_router(
    sensor_routes.router
)


app.include_router(
    batch_routes.router
)


app.include_router(
    report_routes.router
)



@app.get("/")
def root():

    return {

        "system":
        "Coffee AI Analyzer",

        "status":
        "API Running"

    }