# ============================================================
# CoffeeSense AI
# Database Operations Testing
# ============================================================


from backend.database import (
    initialize_database
)


from backend.data_logger import (
    save_quality_record
)


from backend.batch_manager import (
    get_batch_history,
    get_all_batches
)


from backend.report_generator import (
    generate_report
)



from datetime import datetime





# ============================================================
# INITIALIZE DATABASE
# ============================================================


print("\nInitializing Database...")

initialize_database()


print("Database Ready ✅")





# ============================================================
# TEST DATA 01
# PASS SAMPLE
# ============================================================


pass_record = {


    "batch_id":

    "COFFEE-PASS-001",



    "timestamp":

    str(datetime.now()),



    "moisture":

    520,



    "red":

    320,



    "green":

    390,



    "blue":

    330,



    "temperature":

    32,



    "humidity":

    50,



    "status":

    "PASS",



    "quality_score":

    100,



    "confidence":

    100,



    "recommendation":

    "Coffee powder ready for packing."



}





# ============================================================
# TEST DATA 02
# HOLD SAMPLE
# ============================================================



hold_record = {


    "batch_id":

    "COFFEE-HOLD-001",



    "timestamp":

    str(datetime.now()),



    "moisture":

    250,



    "red":

    500,



    "green":

    600,



    "blue":

    520,



    "temperature":

    42,



    "humidity":

    80,



    "status":

    "HOLD",



    "quality_score":

    20,



    "confidence":

    50,



    "recommendation":

    """
    Controlled drying required.
    Maintain 40-45C temperature.
    Reduce humidity below 55%.
    Re-test after recovery.
    """

}





# ============================================================
# SAVE RECORDS
# ============================================================



print("\nSaving PASS batch...")


save_quality_record(
    pass_record
)


print(
    "PASS batch saved ✅"
)





print("\nSaving HOLD batch...")


save_quality_record(
    hold_record
)


print(
    "HOLD batch saved ✅"
)





# ============================================================
# RETRIEVE HISTORY
# ============================================================



print("\n========== BATCH HISTORY ==========")


history = get_batch_history(

    "COFFEE-HOLD-001"

)



for row in history:


    print(row)






# ============================================================
# ALL BATCHES
# ============================================================


print("\n========== AVAILABLE BATCHES ==========")



batches = get_all_batches()



for batch in batches:


    print(
        batch
    )







# ============================================================
# REPORT GENERATION
# ============================================================



print("\n========== QUALITY REPORT ==========")



report = generate_report(

    hold_record

)



print(report)



print("\nDATABASE TEST COMPLETED SUCCESSFULLY ✅")