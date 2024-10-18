from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TokenBase(BaseModel):
    token: str
    user_id: int
    expires_at: datetime

class TokenCreate(TokenBase):
    pass

class TokenUpdate(TokenBase):
    token: Optional[str]
    expires_at: Optional[datetime]

class TokenInDB(TokenBase):
    id: int
    created_at: datetime

class TokenOut(TokenInDB):
    pass