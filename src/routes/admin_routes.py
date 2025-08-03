from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.infra.sqlalchemy.database import get_db
from src.infra.sqlalchemy.repositories.admin_repository import AdminRepository
from src.schemas.admin_schema import AdminCreate, AdminResponse
from src.infra.sqlalchemy.auth import create_access_token, get_current_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.post("", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def create_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    new_admin = AdminRepository(db).create_admin(admin)
    return new_admin

@router.get("/me", response_model=AdminResponse)
def get_admin_me(admin: AdminResponse = Depends(get_current_admin)):
    return admin

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Autentica um administrador e retorna um token JWT.
    """
    repo = AdminRepository(db)

    admin = repo.get_by_name(form_data.username)

    if not admin or not repo.verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de utilizador ou palavra-passe incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": admin.name})

    return {"access_token": access_token, "token_type": "bearer"}
