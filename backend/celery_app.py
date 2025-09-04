import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

celery = Celery(__name__)
celery.conf.broker_url = os.getenv("CELERY_BROKER_URL")
celery.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")

celery.conf.task_routes = {
    "app.tasks.run_weekly_crawl": "crawl-queue",
    "app.tasks.validate_data_task": "validation-queue",
}

@celery.task
def debug_task():
return "Celery is working!"
