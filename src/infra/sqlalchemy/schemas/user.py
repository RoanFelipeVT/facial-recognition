from pydantic import BaseModel, AfterValidator, ValidationError
from typing import Optional, Annotated
from src.infra.sqlalchemy.models.validators.validators import is_char, is_digit


class UserBase(BaseModel):
    name: Annotated[str, AfterValidator(is_char)] 
    cellphone: Annotated[str, AfterValidator(is_digit)]
 

class UserCreate(UserBase):
    # Essa classe é usada para criar um novo usuário, aqui você pode adicionar validações adicionais se necessário
    pass

class UserResponse(UserBase):
    # Essa classe é usada como modelo de resposta para o usuário
    id: int
    image_path: Optional[str] = None
    

    class Config:
        from_attributes = True