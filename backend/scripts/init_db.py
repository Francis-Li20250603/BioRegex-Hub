from app.database import create_db_and_tables, engine
from sqlmodel import Session
from app.models import User
from app.utils.security import get_password_hash

def init_db():
    print("Initializing database...")
    create_db_and_tables()
    
    with Session(engine) as session:
        session.execute("""
            CREATE INDEX IF NOT EXISTS idx_rule_data_type ON rule (data_type);
            CREATE INDEX IF NOT EXISTS idx_rule_region ON rule (region);
            CREATE INDEX IF NOT EXISTS idx_submission_status ON rule_submission (status);
        """)
        session.commit()

        admin_email = "admin@bioregex.com"
        admin_user = session.exec(
            select(User).where(User.email == admin_email)
        ).first()
        
        if not admin_user:
            admin_user = User(
                email=admin_email,
                full_name="Admin User",
                is_admin=True,
                hashed_password=get_password_hash("adminpassword")
            )
            session.add(admin_user)
            session.commit()
            print("Admin user created")
        else:
            print("Admin user already exists")

if __name__ == "__main__":
    init_db()
