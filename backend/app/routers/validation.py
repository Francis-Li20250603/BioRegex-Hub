from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session
from app.database import get_db
from app.models import Rule
from app.tasks import validate_data_task
from celery.result import AsyncResult
from app.utils.file_parsers import parse_file
from app.utils.validators import ks_test
import pandas as pd
import io
import json
from app import crud

router = APIRouter()

@router.post("/")
async def validate_data(
    rule_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Check rule exists
    rule = db.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Parse the uploaded file
    try:
        df = await parse_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    
    # For small files, do in-process; for large, use Celery
    if len(df) < 10000:  # Small file
        # Perform validation
        col_name = df.columns[0]  # Assume first column
        mask = df[col_name].astype(str).str.match(rule.pattern)
        passed = mask.all()
        
        return {
            "passed": bool(passed),
            "invalid_count": int((~mask).sum()),
            "invalid_samples": df[~mask].head(10).to_dict(orient="records")
        }
    else:
        # For large files, use Celery
        data_json = df.to_json(orient="split")
        task = validate_data_task.delay(rule.pattern, data_json)
        return {"task_id": task.id}

@router.get("/result/{task_id}")
def get_validation_result(task_id: str):
    task = AsyncResult(task_id)
    if not task.ready():
        return {"status": "pending"}
    result = task.get()
    return {"status": "completed", "result": result}
