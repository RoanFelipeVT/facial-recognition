from pydantic import BaseModel
from typing import Optional, List, Any

class UserBase(BaseModel):
    name: str
    position: Optional[str] = None
    cellphone: str
    email: str
    

class UserCreate(UserBase):
    # Essa classe é usada para criar um novo usuário, aqui você pode adicionar validações adicionais se necessário
    pass

class UserResponse(UserBase):
    # Aqui você pode adicionar campos adicionais que deseja retornar na resposta
    id: int
    image_path: Optional[str] = None
    pass 
    

    class Config:
        orm_mode = True