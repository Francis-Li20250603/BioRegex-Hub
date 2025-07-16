from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class RuleBase(SQLModel):
    pattern: str = Field(index=True)
    description: str
    data_type: str = Field(index=True)
    region: str = Field(index=True)  # FDA, EMA, HIPAA, etc.
    reference_url: Optional[str] = Field(default=None)

class Rule(RuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    submissions: List["RuleSubmission"] = Relationship(back_populates="rule")

class RuleCreate(RuleBase):
    pass

class RuleRead(RuleBase):
    id: int
    created_at: datetime

class RuleUpdate(SQLModel):
    pattern: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    region: Optional[str] = None
    reference_url: Optional[str] = None

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: str
    is_admin: bool = Field(default=False)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    submissions: List["RuleSubmission"] = Relationship(back_populates="submitter")
    reviews: List["RuleSubmission"] = Relationship(back_populates="reviewer")

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class RuleSubmissionBase(SQLModel):
    pattern: str
    description: str
    data_type: str
    region: str
    reference_path: Optional[str] = None
    submitted_by_id: int = Field(foreign_key="user.id")
    rule_id: Optional[int] = Field(foreign_key="rule.id", default=None)

class RuleSubmission(RuleSubmissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="pending")  # pending, approved, rejected
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_by_id: Optional[int] = Field(foreign_key="user.id", default=None)
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    
    submitter: "User" = Relationship(back_populates="submissions")
    reviewer: Optional["User"] = Relationship(back_populates="reviews")
    rule: Optional["Rule"] = Relationship(back_populates="submissions")

class RuleSubmissionCreate(RuleSubmissionBase):
    pass

class RuleSubmissionRead(RuleSubmissionBase):
    id: int
    status: str
    submitted_at: datetime
    submitted_by: UserRead
    reviewed_by: Optional[UserRead] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    email: Optional[str] = None
