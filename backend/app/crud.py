from sqlmodel import Session, select
from app.models import (
    User, UserCreate, Rule, RuleCreate, 
    RuleSubmission, RuleSubmissionCreate, RuleSubmissionUpdate
)
from app.utils.security import get_password_hash

def get_user_by_email(db: Session, email: str) -> User:
    return db.exec(select(User).where(User.email == email)).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_rule(db: Session, rule: RuleCreate) -> Rule:
    db_rule = Rule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def create_submission(db: Session, submission: RuleSubmissionCreate) -> RuleSubmission:
    db_submission = RuleSubmission(**submission.dict())
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def get_submissions(db: Session, status: str = None, limit: int = 100):
    query = select(RuleSubmission)
    if status:
        query = query.where(RuleSubmission.status == status)
    return db.exec(query.limit(limit)).all()

def get_submission(db: Session, submission_id: int):
    return db.get(RuleSubmission, submission_id)

def update_submission(db: Session, submission_id: int, data: dict):
    submission = db.get(RuleSubmission, submission_id)
    if not submission:
        return None
    
    for key, value in data.items():
        setattr(submission, key, value)
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission
