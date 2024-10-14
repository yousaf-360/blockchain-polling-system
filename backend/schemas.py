from pydantic import BaseModel, Field
from typing import List

class UserCreate(BaseModel):
    username: str = Field(..., example="john_doe")
    password: str = Field(..., example="secure_password")

class UserLogin(BaseModel):
    username: str = Field(..., example="john_doe")
    password: str = Field(..., example="secure_password")

class UserResponse(BaseModel):
    username: str

# Create poll request model
class PollCreate(BaseModel):
    question: str
    options: List[str]  # List of options, initialized with 0 votes