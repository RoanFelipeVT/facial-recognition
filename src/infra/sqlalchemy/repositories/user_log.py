from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from src.infra.sqlalchemy.models.user_log import UserLog

class UserLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_log(self):
        return self.db.query(UserLog).all()


    def create(self, user_id: int, name: str, position: Optional[str], image_path: str, log_time):
        if isinstance(log_time, str):
            log_time = datetime.fromisoformat(log_time)

        new_log = UserLog(
        user_id=user_id,
        user_name=name,
        user_position=position,
        user_image_path=image_path,
        log_time=log_time
        )
        self.db.add(new_log)
        self.db.commit()
        self.db.refresh(new_log)
        return new_log
