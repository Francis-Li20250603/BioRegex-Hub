from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session
from app.database import get_db
from app.models import Rule
from app.tasks import validate_data_task
from celery.result import AsyncResult
from app.utils.file_parsers import parse_file
import pandas as pd
import json
from collections import defaultdict
import re

router = APIRouter()

pattern_cache = defaultdict(dict)

def get_compiled_pattern(pattern: str):
    if pattern not in pattern_cache:
        pattern_cache[pattern] = re.compile(pattern)
    return pattern_cache[pattern]

@router.post("/")
async def validate_data(
    rule_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    rule = db.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    try:
        df = await parse_file(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")

    if len(df) < 10000:
        col_name = df.columns[0]
        compiled_pattern = get_compiled_pattern(rule.pattern)
        mask = df[col_name].apply(lambda x: bool(compiled_pattern.fullmatch(str(x))))
        passed = mask.all()
        return {
            "passed": bool(passed),
            "invalid_count": int((~mask).sum()),
            "invalid_samples": df[~mask].head(10).to_dict(orient="records")
        }
    else:
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
