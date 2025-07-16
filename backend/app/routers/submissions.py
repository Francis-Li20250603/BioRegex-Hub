from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlmodel import Session, select
from app.database import get_db
from app.models import RuleSubmission, RuleSubmissionRead, RuleSubmissionCreate, User
from datetime import datetime
import os
from pathlib import Path
from uuid import uuid4
from app.config import settings
from app.utils.security import get_current_user
from app import crud

router = APIRouter()

def save_upload_file(file: UploadFile) -> str:
    # Create upload directory if not exists
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True, parents=True)
    
    # Generate unique filename
    file_ext = file.filename.split('.')[-1]
    filename = f"{uuid4()}.{file_ext}"
    file_path = upload_dir / filename
    
    # Save file
    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())
    
    return str(file_path.relative_to(settings.BASE_DIR))

@router.post("/", response_model=RuleSubmissionRead)
async def create_submission(
    pattern: str = Form(...),
    description: str = Form(...),
    data_type: str = Form(...),
    region: str = Form(...),
    reference: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Save file if provided
    reference_path = None
    if reference:
        reference_path = save_upload_file(reference)
    
    submission_data = RuleSubmissionCreate(
        pattern=pattern,
        description=description,
        data_type=data_type,
        region=region,
        reference_path=reference_path,
        submitted_by_id=current_user.id
    )
    
    submission = crud.create_submission(db, submission_data)
    return submission

@router.get("/", response_model=List[RuleSubmissionRead])
def list_submissions(
    status: Optional[str] = Query(None, description="Filter by status (pending, approved, rejected)"),
    limit: int = Query(100, description="Limit the number of results"),
    db: Session = Depends(get_db)
):
    return crud.get_submissions(db, status=status, limit=limit)

@router.get("/{submission_id}", response_model=RuleSubmissionRead)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = crud.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission
