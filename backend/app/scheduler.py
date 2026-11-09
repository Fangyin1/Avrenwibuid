import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import SessionLocal
from app.services.scraper import sync_all_sources

log = logging.getLogger("avrwibuid.scheduler")
scheduler = AsyncIOScheduler()

async def scheduled_sync():
    async with SessionLocal() as db:
        results = await sync_all_sources(db)
        log.info("Catalog sync results: %s", results)

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(scheduled_sync, "interval", hours=6, id="catalog-sync", replace_existing=True, max_instances=1)
        scheduler.start()

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
