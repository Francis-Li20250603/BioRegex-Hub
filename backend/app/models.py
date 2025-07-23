from sqlmodel import SQLModel, Field, Relationship, text
from typing import Optional, List
from datetime import datetime
from pydantic import field_validator, model_validator, ConfigDict
import re
import bcrypt


class RuleBase(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    pattern: str = Field(index=True, min_length=1, description="正则表达式模式")
    description: str = Field(min_length=1, description="规则描述")
    data_type: str = Field(index=True, min_length=1, description="数据类型")
    region: str = Field(index=True, min_length=1, description="适用区域（FDA, EMA, HIPAA等）")
    reference_url: Optional[str] = Field(default=None, max_length=2000, description="参考链接")

    @field_validator("pattern")
    def validate_pattern(cls, v):
        if not re.match(r'^[\w\s\d\^\$\*\+\?\.\(\)\[\]\{\}\|\\]+$', v):
            raise ValueError("无效的正则表达式模式")
        return v


class UserBase(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    email: str = Field(unique=True, index=True, description="用户邮箱", max_length=255)
    full_name: str = Field(description="用户全名")
    is_admin: bool = Field(default=False, description="是否为管理员")

    @field_validator('email')
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v


class RuleSubmissionBase(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    pattern: str = Field(description="正则表达式模式")
    description: str = Field(description="规则描述")
    data_type: str = Field(description="数据类型")
    region: str = Field(description="适用区域")
    reference_path: Optional[str] = Field(default=None)
    status: str = Field(default="pending", description="提交状态")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_by_id: int = Field(foreign_key="user.id")
    reviewed_by_id: Optional[int] = Field(foreign_key="user.id", default=None)
    rule_id: Optional[int] = Field(foreign_key="rule.id", default=None)
    reviewed_at: Optional[datetime] = Field(default=None)
    review_notes: Optional[str] = Field(default=None)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(description="加密后的密码")  # 数据库存储哈希密码
    
    submissions: List["RuleSubmission"] = Relationship(
        back_populates="submitter",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.submitted_by_id]"}
    )
    reviews: List["RuleSubmission"] = Relationship(
        back_populates="reviewer",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.reviewed_by_id]"}
    )

    @classmethod
    def create_password_hash(cls, password: str) -> str:
        """生成密码哈希（供UserCreate调用）"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))


class Rule(RuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
        description="创建时间"
    )
    
    submissions: List["RuleSubmission"] = Relationship(
        back_populates="rule",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.rule_id]"}
    )


class RuleSubmission(RuleSubmissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    submitter: "User" = Relationship(
        back_populates="submissions",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.submitted_by_id]"}
    )
    reviewer: Optional["User"] = Relationship(
        back_populates="reviews",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.reviewed_by_id]"}
    )
    rule: Optional[Rule] = Relationship(
        back_populates="submissions",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.rule_id]"}
    )


class RuleCreate(RuleBase):
    pass


class RuleRead(RuleBase):
    id: int
    created_at: datetime


class RuleUpdate(SQLModel):
    model_config = ConfigDict(extra='forbid')
    pattern: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    region: Optional[str] = None
    reference_url: Optional[str] = None


# app/models.py

class UserCreate(UserBase):
    password: str  # 仅用于创建时接收原始密码，不存储到数据库
    is_admin: Optional[bool] = False  # 添加 is_admin 字段，可选




class UserRead(UserBase):
    id: int


class RuleSubmissionCreate(RuleSubmissionBase):
    id: Optional[int] = None
    status: Optional[str] = None
    submitted_at: Optional[datetime] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    rule_id: Optional[int] = None


class RuleSubmissionUpdate(SQLModel):
    model_config = ConfigDict(extra='forbid')
    pattern: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    region: Optional[str] = None
    reference_path: Optional[str] = None
    status: Optional[str] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    rule_id: Optional[int] = None


class RuleSubmissionRead(RuleSubmissionBase):
    id: int
    submitted_by: UserRead
    reviewed_by: Optional[UserRead] = None


class Token(SQLModel):
    model_config = ConfigDict(extra='forbid')
    access_token: str
    token_type: str


class TokenData(SQLModel):
    model_config = ConfigDict(extra='forbid')
    email: Optional[str] = None

