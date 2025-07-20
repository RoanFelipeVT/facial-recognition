from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas.user import UserCreate, UserResponse
from ..repositories.user import UserRepository
from ..auth import get_current_admin
from ..models.admin import Admin as AdminModel 

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    name: str = Form(...),
    position: Optional[str] = Form(None),
    cellphone: str = Form(...),
    email: str = Form(...),
    image_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
) -> UserResponse:
    """
    Cria um novo usuário com reconhecimento facial e armazena as suas informações no banco de dados.
    O arquivo de imagem deve ser enviado como um arquivo multipart/form-data.
    Apenas administradores autenticados podem usar esta rota.
    """
    user_repo = UserRepository(db)
    try:
        user_data = UserCreate(name=name, position=position, cellphone=cellphone, email=email)
        image_content = await image_file.read()
        new_user = user_repo.create_user(user_data, image_content)
        return new_user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao criar usuário: {e}")

@router.get("/{user_id}", response_model=UserResponse)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db), current_admin: AdminModel = Depends(get_current_admin)):
    user_repo = UserRepository(db)
    user = user_repo.get_user(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get("/", response_model=List[UserResponse])
def get_all_users_endpoint(db: Session = Depends(get_db), current_admin: AdminModel = Depends(get_current_admin)):
    user_repo = UserRepository(db)
    users = user_repo.get_users()  # Sem skip e limit
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db), current_admin: AdminModel = Depends(get_current_admin)):
    user_repo = UserRepository(db)
    if not user_repo.delete_user(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or could not be deleted")
    return {"message": "User deleted successfully"}
