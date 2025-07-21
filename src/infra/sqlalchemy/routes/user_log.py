from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.user_log import UserLogResponse, UserLog
from ..repositories.user_log import UserLogRepository
from ..auth import get_current_admin
from ..models.admin import Admin as AdminModel

router = APIRouter(prefix="/users_log", tags=["UsersLog"])



@router.post("/", response_model=UserLog, status_code=201)
def create_user_log_endpoint(
    user_id: int,
    log_time: str,
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
) -> UserLog:
    """
    Cria um novo log de usuário.
    Apenas administradores autenticados podem usar esta rota.
    """
    user_log_repo = UserLogRepository(db)
    return user_log_repo.create(user_id, log_time)


@router.get("/")
def get_user_log_endpoint(
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
):
    user_log_repo = UserLogRepository(db)
    user_logs = user_log_repo.get_user_log_with_user_data()
    return user_logs
