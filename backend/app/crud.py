from sqlmodel import Session, select
from app.models import User, UserCreate, Rule, RuleCreate, RuleSubmission, RuleSubmissionCreate, RuleSubmissionUpdate
from app.utils.security import get_password_hash
from collections import defaultdict

class RuleUnionFind:
    def __init__(self):
        self.parent = {}
        self.rank = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        elif self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        rootX = self.find(x)
        rootY = self.find(y)
        if rootX != rootY:
            if self.rank[rootX] > self.rank[rootY]:
                self.parent[rootY] = rootX
            elif self.rank[rootX] < self.rank[rootY]:
                self.parent[rootX] = rootY
            else:
                self.parent[rootY] = rootX
                self.rank[rootX] += 1

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

def get_related_rules(db: Session, rule_id: int):
    uf = RuleUnionFind()
    rules = db.exec(select(Rule)).all()
    type_groups = defaultdict(list)
    for rule in rules:
        type_groups[rule.data_type].append(rule.id)
    for _, ids in type_groups.items():
        for i in range(1, len(ids)):
            uf.union(ids[0], ids[i])
    root = uf.find(rule_id)
    return [r for r in rules if uf.find(r.id) == root]
