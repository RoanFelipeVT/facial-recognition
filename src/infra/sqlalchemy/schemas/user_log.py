from pydantic import BaseModel, AfterValidator, ValidationError
from typing import Optional, Annotated
from datetime import datetime
from src.infra.sqlalchemy.models.validators.validators import is_char


class UserLog(BaseModel):
    id: int
    log_time: datetime
    user_name: str
    user_position: Optional[str]
    user_image_path: str

    class Config:
        orm_mode = True
