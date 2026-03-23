from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="User Microservice", version="1.0.0")

# --- DATA MODELS ---
class UserBase(BaseModel):
    name: str
    email: str
    role: str = "customer"

class User(UserBase):
    id: int

# --- MOCK DATABASE ---
users_db = [
    User(id=1, name="John Doe", email="john@example.com", role="customer"),
    User(id=2, name="Jane Smith", email="admin@example.com", role="admin")
]

# --- ENDPOINTS ---

@app.get("/api/users", response_model=List[User])
def get_all_users():
    """Retrieve all users"""
    return users_db

@app.get("/api/users/{user_id}", response_model=User)
def get_user(user_id: int):
    """Retrieve a specific user by ID"""
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/api/users", response_model=User, status_code=201)
def create_user(user_in: UserBase):
    """Create a new user"""
    new_id = max((u.id for u in users_db), default=0) + 1
    new_user = User(id=new_id, **user_in.model_dump())
    users_db.append(new_user)
    return new_user

@app.delete("/api/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    """Delete a user"""
    global users_db
    users_db = [u for u in users_db if u.id != user_id]
    return None