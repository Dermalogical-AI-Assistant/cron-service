import schedule
import asyncio
import time
from datetime import datetime
import pytz
from db import database

STATUS_ACTIVE = "ACTIVE"
STATUS_EXPIRED = "EXPIRED"

async def handle_discount_status_update():
    await database.connect()  # ✅ Ensure connection is open
    now = datetime.now(pytz.timezone("Asia/Bangkok"))

    query_activate = """
        UPDATE discount
        SET status = :new_status
        WHERE start_time <= now()
          AND end_time >= now()
          AND status IS DISTINCT FROM :new_status
    """

    query_expire = """
        UPDATE discount
        SET status = :new_status
        WHERE end_time < now()
          AND status IS DISTINCT FROM :new_status
    """

    await asyncio.gather(
        database.execute(query=query_activate, values={
            "new_status": STATUS_ACTIVE
        }),
        database.execute(query=query_expire, values={
            "new_status": STATUS_EXPIRED
        })
    )
    print(f"[{now}] Discount statuses updated.")
    
# Wrapper for asyncio
def job_wrapper():
    asyncio.run(handle_discount_status_update())

def main():
    # Schedule the job to run every day at 9:47 AM
    schedule.every().day.at("07:00").do(job_wrapper)

    print("Scheduler started (schedule lib). Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
