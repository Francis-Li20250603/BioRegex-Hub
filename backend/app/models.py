from sqlmodel import SQLModel, Field, Relationship, text
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from pydantic import field_validator, model_validator, ConfigDict
import re
import bcrypt


# 解决同一文件内的类型提示问题（无需导入自身，直接使用字符串引用）
if TYPE_CHECKING:
    # 移除从自身导入的语句，改用字符串类型提示
    pass


# ------------------------------
# 基础模型（先定义基础模型，避免依赖问题）
# ------------------------------
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


# ------------------------------
# 数据库表模型（核心模型）
# ------------------------------
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(description="加密后的密码")
    
    # 关系定义：使用字符串引用避免同一文件内的依赖问题
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


class Rule(RuleBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"server_default": text("CURRENT_TIMESTAMP")},
        description="创建时间"
    )
    
    # 关系定义：使用字符串引用
    submissions: List["RuleSubmission"] = Relationship(
        back_populates="rule",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.rule_id]"}
    )


class RuleSubmission(RuleSubmissionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 关系定义：使用字符串引用
    submitter: "User" = Relationship(
        back_populates="submissions",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.submitted_by_id]"}
    )
    reviewer: Optional["User"] = Relationship(
        back_populates="reviews",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.reviewed_by_id]"}
    )
    rule: Optional["Rule"] = Relationship(
        back_populates="submissions",
        sa_relationship_kwargs={"foreign_keys": "[RuleSubmission.rule_id]"}
    )


# ------------------------------
# 数据传输模型（CRUD操作使用）
# ------------------------------
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


class RuleSubmissionCreate(RuleSubmissionBase):
    # 创建时不需要ID和自动生成的字段
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
    # 读取时需要包含ID和关联信息
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

