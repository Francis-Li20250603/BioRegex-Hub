from sqlmodel import SQLModel, Field, Relationship, text
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
# 替换 Pydantic 导入（关键修正）
from pydantic import field_validator, model_validator, ConfigDict
import re
import bcrypt


if TYPE_CHECKING:
    from .models import RuleSubmission


class RuleBase(SQLModel):
    # 替换旧的 class Config 为 ConfigDict（Pydantic v2 兼容）
    model_config = ConfigDict(extra='forbid')
    
    pattern: str = Field(index=True, min_length=1, description="正则表达式模式")
    description: str = Field(min_length=1, description="规则描述")
    data_type: str = Field(index=True, min_length=1, description="数据类型")
    region: str = Field(index=True, min_length=1, description="适用区域")
    reference_url: Optional[str] = Field(default=None, max_length=2000)

    # 替换 @validator 为 @field_validator（Pydantic v2 语法）
    @field_validator("pattern")
    def validate_pattern(cls, v):
        if not re.match(r'^[\w\s\d\^\$\*\+\?\.\(\)\[\]\{\}\|\\]+$', v):
            raise ValueError("无效的正则表达式模式")
        return v


class UserBase(SQLModel):
    model_config = ConfigDict(extra='forbid')
    
    email: str = Field(unique=True, index=True, max_length=255)
    full_name: str = Field(description="用户全名")
    is_admin: bool = Field(default=False)

    # 替换 @validator 为 @field_validator
    @field_validator('email')
    def validate_email(cls, v):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, v):
            raise ValueError('Invalid email format')
        return v


# 以下模型定义保持不变，但确保使用 model_config 替代 class Config
class Rule(RuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")}
    )
    submissions: List["RuleSubmission"] = Relationship(
        back_populates="rule",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.rule_id]"}
    )


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field()
    
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
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))


# 其余模型（RuleSubmission、各种Create/Read/Update类）保持不变，但确保添加 model_config
class RuleSubmission(SQLModel, table=True):
    model_config = ConfigDict(extra='forbid')
    
    id: Optional[int] = Field(default=None, primary_key=True)
    pattern: str = Field()
    description: str = Field()
    data_type: str = Field()
    region: str = Field()
    reference_path: Optional[str] = Field(default=None)
    status: str = Field(default="pending")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_by_id: int = Field(foreign_key="user.id")
    reviewed_by_id: Optional[int] = Field(foreign_key="user.id", default=None)
    rule_id: Optional[int] = Field(foreign_key="rule.id", default=None)
    reviewed_at: Optional[datetime] = Field(default=None)
    review_notes: Optional[str] = Field(default=None)
    
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
    model_config = ConfigDict(extra='forbid')


class RuleRead(RuleBase):
    model_config = ConfigDict(extra='forbid')
    id: int
    created_at: datetime


class RuleUpdate(SQLModel):
    model_config = ConfigDict(extra='forbid')
    pattern: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    region: Optional[str] = None
    reference_url: Optional[str] = None


class UserCreate(UserBase):
    model_config = ConfigDict(extra='forbid')
    password: str

    @model_validator(mode='before')
    def hash_password(cls, values):
        if 'password' in values:
            values['hashed_password'] = User.create_password_hash(values['password'])
            del values['password']
        return values


class UserRead(UserBase):
    model_config = ConfigDict(extra='forbid')
    id: int


class RuleSubmissionCreate(SQLModel):
    model_config = ConfigDict(extra='forbid')
    pattern: str
    description: str
    data_type: str
    region: str
    reference_path: Optional[str] = None
    submitted_by_id: int


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


class Token(SQLModel):
    model_config = ConfigDict(extra='forbid')
    access_token: str
    token_type: str


class TokenData(SQLModel):
    model_config = ConfigDict(extra='forbid')
    email: Optional[str] = None
