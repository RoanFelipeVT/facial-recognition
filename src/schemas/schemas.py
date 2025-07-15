from pydantic import BaseModel
from typing import Optional

class AdminLogin(BaseModel):
    name: str
    password: str

class AdminCreate(BaseModel):
    name: str
    password: str

class Admin(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True
        
class User(BaseModel):
    name: str
    university_id: str
    image_path: str
    encoding: dict

    class Config:
        orm_mode = True