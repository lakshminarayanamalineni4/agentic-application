from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, ConfigDict

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    mobile: str = Field(..., min_length=10)
    email: EmailStr
    password: str = Field(...,min_length=8)

class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    mobile: str = Field(min_length=10)
    email: EmailStr
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    name: str
    mobile: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    # The user message must be present and non-empty.
    # ... means the field is required.
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    # The API response contains a single answer string.
    answer: str
