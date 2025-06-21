from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
import asyncio
from db import database

# Status values
STATUS_ACTIVE = "ACTIVE"
STATUS_EXPIRED = "EXPIRED"

# Function to update discount statuses
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
    await database.disconnect()

# Run the scheduler
def main():
    scheduler = AsyncIOScheduler(timezone="Asia/Bangkok")
    scheduler.add_job(handle_discount_status_update, CronTrigger(hour=7, minute=0))

    async def start():
        await database.connect()
        scheduler.start()
        print("Scheduler started. Running until manually stopped.")

    asyncio.get_event_loop().run_until_complete(start())
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    print("Cron service is running.")
    main()
