from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud
from app.schemas import RuleSubmissionRead
from app.dependencies import get_db, get_current_admin
from app.models import User

router = APIRouter()

@router.get("/submissions/pending", response_model=list[RuleSubmissionRead])
def get_pending_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    return crud.get_submissions(db, status="pending")
