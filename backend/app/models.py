from sqlmodel import SQLModel, Field, Relationship, text
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import validator, model_validator
import re
import bcrypt


# 解决循环导入问题
if TYPE_CHECKING:
    from .models import RuleSubmission  # 调整为正确的导入路径


class RuleBase(SQLModel):
    pattern: str = Field(index=True, min_length=1, description="正则表达式模式")
    description: str = Field(min_length=1, description="规则描述")
    data_type: str = Field(index=True, min_length=1, description="数据类型")
    region: str = Field(index=True, min_length=1, description="适用区域（FDA, EMA, HIPAA等）")
    reference_url: Optional[str] = Field(default=None, max_length=2000, description="参考链接")


    @validator("pattern")
    def validate_pattern(cls, v):
        if not re.match(r'^[\w\s\d\^\$\*\+\?\.\(\)\[\]\{\}\|\\]+$', v):
            raise ValueError("无效的正则表达式模式")
        return v


class Rule(RuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
        description="创建时间"
    )
    # 使用 sa_relationship_kwargs 传递原生SQLAlchemy参数
    submissions: List["RuleSubmission"] = Relationship(
        back_populates="rule",
        sa_relationship_kwargs={
            "foreign_keys": "[RuleSubmission.rule_id]"
        }
    )


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, description="用户邮箱", max_length=255)
    full_name: str = Field(description="用户全名")
    is_admin: bool = Field(default=False, description="是否为管理员")


    @validator('email')
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(description="加密后的密码")
    
    # 明确两个关系对应的外键（使用SQLAlchemy原生参数）
    submissions: List["RuleSubmission"] = Relationship(
        back_populates="submitter",
        sa_relationship_kwargs={
            "foreign_keys": "[RuleSubmission.submitted_by_id]"
        }
    )
    reviews: List["RuleSubmission"] = Relationship(
        back_populates="reviewer",
        sa_relationship_kwargs={
            "foreign_keys": "[RuleSubmission.reviewed_by_id]"
        }
    )


    @classmethod
    def create_password_hash(cls, password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))


class RuleSubmission(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pattern: str = Field(description="正则表达式模式")
    description: str = Field(description="规则描述")
    data_type: str = Field(description="数据类型")
    region: str = Field(description="适用区域")
    reference_path: Optional[str] = Field(default=None)
    status: str = Field(default="pending", description="提交状态")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 外键定义
    submitted_by_id: int = Field(foreign_key="user.id")
    reviewed_by_id: Optional[int] = Field(foreign_key="user.id", default=None)
    rule_id: Optional[int] = Field(foreign_key="rule.id", default=None)
    
    reviewed_at: Optional[datetime] = Field(default=None)
    review_notes: Optional[str] = Field(default=None)
    
    # 明确关系对应的外键
    submitter: "User" = Relationship(
        back_populates="submissions",
        sa_relationship_kwargs={
            "foreign_keys": "[RuleSubmission.submitted_by_id]"
        }
    )
    reviewer: Optional["User"] = Relationship(
        back_populates="reviews",
        sa_relationship_kwargs={
            "foreign_keys": "[RuleSubmission.reviewed_by_id]"
        }
    )
    rule: Optional[Rule] = Relationship(
        back_populates="submissions",
        sa_relationship_kwargs={
            "foreign_keys": "[RuleSubmission.rule_id]"
        }
    )


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


    @model_validator(mode='before')
    def hash_password(cls, values):
        if 'password' in values:
            values['hashed_password'] = User.create_password_hash(values['password'])
            del values['password']
        return values


class UserRead(UserBase):
    id: int


class RuleSubmissionCreate(SQLModel):
    pattern: str
    description: str
    data_type: str
    region: str
    reference_path: Optional[str] = None
    submitted_by_id: int


class RuleSubmissionUpdate(SQLModel):
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


class RuleSubmissionRead(RuleSubmissionCreate):
    id: int
    status: str
    submitted_at: datetime
    submitted_by: UserRead
    reviewed_by: Optional[UserRead] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    rule_id: Optional[int] = None


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    email: Optional[str] = None
    
