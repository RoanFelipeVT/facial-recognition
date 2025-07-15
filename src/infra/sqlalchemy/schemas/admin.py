from pydantic import BaseModel
from typing import Optional

class AdminBase(BaseModel):
    name: str

class AdminCreate(AdminBase):
    password: str

class AdminResponse(AdminBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    name: Optional[str] = None