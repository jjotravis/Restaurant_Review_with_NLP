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

class AdminResponse(AdminBase):
    admin_id: int

    class Config:
        from_attributes = True
