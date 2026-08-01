from backend.explainable_ai import analyze_sensor_impact

from backend.simulation_engine import simulate_moisture_recovery



result = analyze_sensor_impact(

    moisture=250,

    red=500,

    green=600,

    blue=520,

    temperature=42,

    humidity=80

)


print("\n========== AI EXPLANATION ==========")


print(
    "Main Cause:",
    result["main_cause"]
)


for item in result["explanations"]:

    print(
        item
    )




print("\n========== RECOVERY SIMULATION ==========")



simulation = simulate_moisture_recovery(

    250

)



print(

simulation

)