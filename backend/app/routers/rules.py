from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.database import get_db
from app.models import Rule, RuleRead, RuleCreate, RuleUpdate
from typing import List, Optional


router = APIRouter()


@router.get("/", response_model=List[RuleRead])
def list_rules(
    region: Optional[str] = Query(None, description="Filter by regulatory region (e.g., FDA, EMA)"),
    data_type: Optional[str] = Query(None, description="Filter by data type (e.g., Patient ID)"),
    limit: int = Query(100, description="Limit the number of results"),
    db: Session = Depends(get_db)
):
    query = select(Rule)
    if region:
        query = query.where(Rule.region == region)
    if data_type:
        query = query.where(Rule.data_type.ilike(f"%{data_type}%"))
    return db.exec(query.limit(limit)).all()


@router.get("/{rule_id}", response_model=RuleRead)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.post("/", response_model=RuleRead, status_code=201)  # 明确指定201状态码
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)):
    db_rule = Rule(** rule.model_dump())  # 使用model_dump()替代deprecated的dict()
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.put("/{rule_id}", response_model=RuleRead)
def update_rule(rule_id: int, rule: RuleUpdate, db: Session = Depends(get_db)):
    db_rule = db.get(Rule, rule_id)
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    update_data = rule.model_dump(exclude_unset=True)  # 使用model_dump()
    for key, value in update_data.items():
        setattr(db_rule, key, value)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.get(Rule, rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted"}
