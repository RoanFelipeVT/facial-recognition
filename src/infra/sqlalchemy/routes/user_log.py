from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.user_log import UserLog
from ..repositories.user_log import UserLogRepository
from ..auth import get_current_admin
from ..models.admin import Admin as AdminModel

router = APIRouter(prefix="/users_log", tags=["UsersLog"])

@router.get("/", response_model=List[UserLog])
def get_user_log_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: AdminModel = Depends(get_current_admin)
):
    user_log_repo = UserLogRepository(db)
    user_logs = user_log_repo.get_user_log(skip=skip, limit=limit)
    return user_logs
