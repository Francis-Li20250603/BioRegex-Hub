from celery import Celery

celery = Celery(
    "bioregex",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

@celery.task
def debug_task():
    return "Celery is working!"

@celery.task
def run_weekly_crawl():
    # TODO: replace with actual crawling logic (FDA/EMA parsers)
    return {"status": "ok", "crawled": 0}
