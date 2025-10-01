"""Example FastAPI application for testing Spout."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Example API", version="1.0.0")


class User(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None


class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World"}


@app.get("/users", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 100):
    """Get list of users."""
    # Mock data
    return [
        User(id=1, name="John Doe", email="john@example.com", age=30),
        User(id=2, name="Jane Smith", email="jane@example.com", age=25),
    ]


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """Get a specific user by ID."""
    if user_id == 1:
        return User(id=1, name="John Doe", email="john@example.com", age=30)
    else:
        raise HTTPException(status_code=404, detail="User not found")


@app.post("/users", response_model=User)
async def create_user(user: UserCreate):
    """Create a new user."""
    new_user = User(id=999, **user.dict())
    return new_user


@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate):
    """Update an existing user."""
    # Mock update
    updated_user = User(
        id=user_id,
        name=user.name or "Updated Name",
        email=user.email or "updated@example.com",
        age=user.age,
    )
    return updated_user


@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    """Delete a user."""
    return {"message": f"User {user_id} deleted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
