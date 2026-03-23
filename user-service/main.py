from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="User Service", version="1.0")

# Example Data Model
class User(BaseModel):
    id: int
    name: str
    email: str

# Mock Database
db = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

@app.get("/")
def read_users():
    return {"users": db}

@app.get("/{user_id}")
def read_user(user_id: int):
    user = next((u for u in db if u["id"] == user_id), None)
    return user if user else {"error": "User not found"}

# To run this specific service:
# uvicorn main:app --reload --port 8001