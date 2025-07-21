from pydantic import BaseModel, AfterValidator, ValidationError
from typing import Optional, Annotated
from datetime import datetime
from src.infra.sqlalchemy.models.validators.validators import is_char


class UserLog(BaseModel):
    id: int
    log_time: datetime

    class Config:
        orm_mode = True
