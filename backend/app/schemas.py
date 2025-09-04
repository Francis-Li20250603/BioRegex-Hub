# backend/app/schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class RuleBase(BaseModel):
    pattern: str
    description: str
    data_type: str
    region: str
    reference_url: Optional[str] = None

class RuleCreate(RuleBase):
    pass

class RuleRead(RuleBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class RuleSubmissionBase(BaseModel):
    pattern: str
    description: str
    data_type: str
    region: str
    reference_url: Optional[str] = None

class RuleSubmissionCreate(RuleSubmissionBase):
    pass

class RuleSubmissionRead(RuleSubmissionBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True
