from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import List

app = FastAPI(title="User Microservice", version="1.0.0")

SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False, default="customer")


Base.metadata.create_all(bind=engine)


class UserBase(BaseModel):
    name: str
    email: str
    role: str = "customer"

    @field_validator("name")
    @classmethod
    def validate_name_non_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty")
        return value.strip()

    @field_validator("email")
    @classmethod
    def validate_email_contains_at(cls, value: str) -> str:
        # Keep validation simple per project requirement: email must include '@'.
        cleaned = value.strip()
        if "@" not in cleaned:
            raise ValueError("Email must contain '@'")
        return cleaned

    @field_validator("role")
    @classmethod
    def validate_role_allowed(cls, value: str) -> str:
        allowed_roles = {"customer", "admin", "client"}
        cleaned = value.strip().lower()
        if cleaned not in allowed_roles:
            raise ValueError("Role must be either 'customer', 'admin', or 'client'")
        return cleaned


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_users_if_empty():
    db = SessionLocal()
    try:
        if db.query(DBUser).count() == 0:
            db.add_all([
                DBUser(name="John Doe", email="john@example.com", role="customer"),
                DBUser(name="Jane Smith", email="admin@example.com", role="admin"),
            ])
            db.commit()
    finally:
        db.close()


seed_users_if_empty()


@app.get("/api/users", response_model=List[User])
def get_all_users(db: Session = Depends(get_db)):
    return db.query(DBUser).all()


@app.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/api/users", response_model=User, status_code=201)
def create_user(user_in: UserBase, db: Session = Depends(get_db)):
    new_user = DBUser(**user_in.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.put("/api/users/{user_id}", response_model=User)
def update_user(user_id: int, user_in: UserBase, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = user_in.name
    user.email = user_in.email
    user.role = user_in.role
    
    db.commit()
    db.refresh(user)
    return user


@app.delete("/api/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None