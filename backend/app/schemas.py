# backend/app/schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# -------------------------
# User schemas
# -------------------------
class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True

# For JWT auth
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    sub: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# -------------------------
# Rule schemas
# -------------------------
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

# -------------------------
# Rule submission schemas
# -------------------------
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

# -------------------------
# Validation schemas
# -------------------------
class ValidationRequest(BaseModel):
    file_path: str
    rule_id: int

class ValidationResult(BaseModel):
    rule_id: int
    valid: bool
    message: Optional[str] = None

