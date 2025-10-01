"""Example Django Ninja application for testing Spout."""

from typing import List, Optional

from ninja import NinjaAPI
from pydantic import BaseModel

api = NinjaAPI(title="Example Ninja API", version="1.0.0")


class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None


class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None


@api.get("/")
def root(request):
    """Root endpoint."""
    return {"message": "Hello from Django Ninja"}


@api.get("/users", response=List[User])
def get_users(request, skip: int = 0, limit: int = 100):
    """Get list of users."""
    # Mock data
    return [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
    ]


@api.get("/users/{user_id}", response=User)
def get_user(request, user_id: int):
    """Get a specific user by ID."""
    if user_id == 1:
        return {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30}
    else:
        return api.create_response(request, {"error": "User not found"}, status=404)


@api.post("/users", response=User)
def create_user(request, user: UserCreate):
    """Create a new user."""
    new_user = {"id": 999, **user.dict()}
    return new_user


@api.delete("/users/{user_id}")
def delete_user(request, user_id: int):
    """Delete a user."""
    return {"message": f"User {user_id} deleted"}
