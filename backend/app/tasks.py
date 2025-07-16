from celery import shared_task
import logging
from app.utils.crawlers import crawl_fda, crawl_ema
from app.database import get_db
from sqlmodel import Session, select, create_engine
from app.config import settings
import pandas as pd
import json
import re

logger = logging.getLogger(__name__)

@shared_task
def validate_data_task(pattern: str, data_json: str):
    try:
        # Convert JSON back to DataFrame
        data = json.loads(data_json)
        df = pd.DataFrame(data["data"], columns=data["columns"])
        
        # Perform validation on first column
        col_name = df.columns[0]
        mask = df[col_name].astype(str).str.match(pattern)
        passed = mask.all()
        
        return {
            "passed": bool(passed),
            "invalid_count": int((~mask).sum()),
            "invalid_samples": df[~mask].head(10).to_dict(orient="records")
        }
    except Exception as e:
        logger.exception("Validation task failed")
        return {"error": str(e)}

@shared_task
def run_weekly_crawl():
    logger.info("Running weekly regulatory crawl")
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        fda_rules = crawl_fda()
        ema_rules = crawl_ema()
        
        # Create report
        report = {
            "fda_rules_added": len(fda_rules),
            "ema_rules_added": len(ema_rules),
            "total_added": len(fda_rules) + len(ema_rules)
        }
        
        logger.info(f"Crawl completed: {report}")
        return report
    except Exception as e:
        logger.exception("Crawl task failed")
        return {"error": str(e)}
