from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- 1. SQLITE DATABASE SETUP ---
# This creates a local file named 'users.db' in your folder
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 2. DATABASE MODEL (SQLAlchemy) ---
class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="customer")

# Create the database tables automatically
Base.metadata.create_all(bind=engine)

# --- 3. PYDANTIC MODELS (For FastAPI) ---
class UserBase(BaseModel):
    name: str
    email: str
    role: str = "customer"

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True

# --- 4. FASTAPI APP ---
app = FastAPI(title="User Microservice (SQLite)", version="1.0.0")

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 5. ENDPOINTS ---
@app.get("/api/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    """Retrieve all users directly from the SQLite database"""
    return db.query(DBUser).all()

@app.post("/api/users", response_model=UserResponse, status_code=201)
def create_user(user: UserBase, db: Session = Depends(get_db)):
    """Save a new user to the SQLite database"""
    db_user = DBUser(name=user.name, email=user.email, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user