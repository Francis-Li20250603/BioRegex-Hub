from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint
from typing import Optional, List
from datetime import datetime
from pydantic import validator
import re

# ---------------
# 基础模型
# ---------------

class RuleBase(SQLModel):
    pattern: str = Field(index=True, min_length=1, description="正则表达式模式")
    description: str = Field(min_length=1, description="规则描述")
    data_type: str = Field(index=True, min_length=1, description="数据类型")
    region: str = Field(index=True, min_length=1, description="适用区域（FDA, EMA, HIPAA等）")
    reference_url: Optional[str] = Field(default=None, max_length=2000, description="参考链接")

    @validator("pattern")
    def validate_pattern(cls, v):
        """验证正则表达式格式"""
        if not re.match(r'^[\w\s\d\^\$\*\+\?\.\(\)\[\]\{\}\|\\]+$', v):
            raise ValueError("无效的正则表达式模式")
        return v

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, description="用户邮箱")
    full_name: str = Field(description="用户全名")
    is_admin: bool = Field(default=False, description="是否为管理员")

class RuleSubmissionBase(SQLModel):
    pattern: str = Field(description="提交的正则表达式模式")
    description: str = Field(description="提交的规则描述")
    data_type: str = Field(description="提交的数据类型")
    region: str = Field(description="提交的适用区域")
    reference_path: Optional[str] = Field(default=None, description="参考文件路径")
    submitted_by_id: int = Field(foreign_key="user.id", description="提交用户ID")
    rule_id: Optional[int] = Field(foreign_key="rule.id", default=None, description="关联规则ID")

# ---------------
# 数据库表模型
# ---------------

class Rule(RuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"},
        description="创建时间"
    )
    submissions: List["RuleSubmission"] = Relationship(back_populates="rule")

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(description="加密后的密码")
    submissions: List["RuleSubmission"] = Relationship(back_populates="submitter")
    reviews: List["RuleSubmission"] = Relationship(back_populates="reviewer")

class RuleSubmission(RuleSubmissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: str = Field(default="pending", description="提交状态：pending, approved, rejected")
    submitted_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": "CURRENT_TIMESTAMP"},
        description="提交时间"
    )
    reviewed_by_id: Optional[int] = Field(foreign_key="user.id", default=None, description="审核用户ID")
    reviewed_at: Optional[datetime] = Field(default=None, description="审核时间")
    review_notes: Optional[str] = Field(default=None, description="审核备注")
    
    submitter: "User" = Relationship(back_populates="submissions")
    reviewer: Optional["User"] = Relationship(back_populates="reviews")
    rule: Optional["Rule"] = Relationship(back_populates="submissions")
    
    __table_args__ = (
        UniqueConstraint("pattern", "submitted_by_id"),  # 避免同一用户重复提交相同模式
    )

# ---------------
# Pydantic 数据传输模型
# ---------------

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

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

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

# ---------------
# 认证模型
# ---------------

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    email: Optional[str] = None
