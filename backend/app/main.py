from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import rules, submissions, auth, validation, admin
from app.database import engine, get_db, create_db_and_tables
from sqlmodel import Session
from contextlib import asynccontextmanager
from app.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    create_db_and_tables()
    yield

app = FastAPI(
    title="BioRegex-Hub API",
    description="API for BioRegex-Hub: Standard Regex Knowledge Base for Biostatistics and Actuarial Science",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(rules.router, prefix="/rules", tags=["Rules"])
app.include_router(submissions.router, prefix="/submissions", tags=["Submissions"])
app.include_router(validation.router, prefix="/validate", tags=["Validation"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

@app.get("/")
def read_root():
    return {"message": "Welcome to BioRegex-Hub API"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
