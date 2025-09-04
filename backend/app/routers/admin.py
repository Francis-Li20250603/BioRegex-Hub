from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_db
from app.models import RuleSubmission, Rule, User, RuleSubmissionRead, RuleCreate
from datetime import datetime
from app.utils.security import get_current_admin
from app import crud

router = APIRouter()

@router.post("/submissions/{submission_id}/approve", response_model=RuleSubmissionRead)
def approve_submission(
    submission_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    submission = crud.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    rule_data = RuleCreate(
        pattern=submission.pattern,
        description=submission.description,
        data_type=submission.data_type,
        region=submission.region,
        reference_url=submission.reference_path
    )
    rule = crud.create_rule(db, rule_data)
    submission = crud.update_submission(
        db,
        submission_id,
        {"status": "approved", "reviewed_by_id": current_user.id, "reviewed_at": datetime.utcnow()}
    )
    return submission

@router.post("/submissions/{submission_id}/reject", response_model=RuleSubmissionRead)
def reject_submission(
    submission_id: int,
    reason: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    submission = crud.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    submission = crud.update_submission(
        db,
        submission_id,
        {
            "status": "rejected",
            "reviewed_by_id": current_user.id,
            "reviewed_at": datetime.utcnow(),
            "review_notes": reason
        }
    )
    return submission

@router.get("/submissions/pending", response_model=list[RuleSubmissionRead])
def get_pending_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
return crud.get_submissions(db, status="pending")
