from pydantic import BaseModel, AfterValidator, ValidationError
from typing import Optional, Annotated
from src.infra.sqlalchemy.models.validators.validators import is_char, is_digit


class UserBase(BaseModel):
    name: Annotated[str, AfterValidator(is_char)] 
    position: Optional[str] = None
    cellphone: Annotated[str, AfterValidator(is_digit)]
    email: str



    

class UserCreate(UserBase):
    # Essa classe é usada para criar um novo usuário, aqui você pode adicionar validações adicionais se necessário
    pass

class UserResponse(UserBase):
    # Aqui você pode adicionar campos adicionais que deseja retornar na resposta
    id: int
    image_path: Optional[str] = None
     
    

    class Config:
        orm_mode = True