from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    password: str
    review_count: int = 0
    role: str

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    user_id: int
    username: str
    password: str
    review_count: int
    role: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    review_count: int
    role: str

    class Config:
        from_attributes = True
