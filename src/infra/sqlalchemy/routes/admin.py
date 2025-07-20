from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.admin import AdminCreate, AdminResponse, Token
from ..repositories.admin import AdminRepository
from ..auth import get_current_admin, verify_password, create_access_token, get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from ..models.admin import Admin

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/register", response_model=AdminResponse)
def register_admin(admin: AdminCreate, db: Session = Depends(get_db)) -> AdminResponse:
    """Cria um novo administrador no sistema.
    Apenas administradores autenticados podem usar esta rota."""
    admin_repo = AdminRepository(db)
    db_admin = admin_repo.get_admin_by_name(admin.name)
    if db_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin already registered")
    return admin_repo.create_admin(admin)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    
    """Gera um token de acesso para o administrador autenticado."""
    """    Verifica as credenciais do administrador e gera um token JWT.
    O token é usado para autenticação em rotas protegidas."""

    # Esse condicional é para garantir que o nome de usuário e senha sejam fornecidos
    # Isso é necessário porque o OAuth2PasswordRequestForm espera esses campos
    if not form_data.username or not form_data.password:        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required",
        )   
    admin_repo = AdminRepository(db)
    admin = admin_repo.get_admin_by_name(form_data.username)
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


"""@router.post("/initial-setup", response_model=AdminResponse, summary="Cria o primeiro admin (USE COM CAUTELA)")
def create_initial_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    admin_repo = AdminRepository(db)
    if admin_repo.get_admin_by_name(admin.name):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin already exists.")

    # Verifique se já existe algum admin para evitar múltiplos administradores iniciais
    # Isso é uma medida de segurança. Em produção, você pode remover esta rota
    # ou ter um mecanismo mais robusto para criação do primeiro admin.
    if db.query(Admin).first():
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An admin already exists. Use the /token endpoint to login.")

    return admin_repo.create_admin(admin)
"""