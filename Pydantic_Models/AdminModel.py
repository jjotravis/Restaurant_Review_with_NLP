from typing import Optional
from pydantic import BaseModel

class AdminBase(BaseModel):
    username: str
    password: str
    name: Optional[str] = "Captain"
    role: Optional[str] = "ADMIN"

class AdminCreate(AdminBase):
    pass

class AdminUpdate(AdminBase):
    admin_id: int

class AdminResponse(BaseModel):
    admin_id: int
    name: str
    role: str

    class Config:
        from_attributes = True
