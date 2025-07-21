from sqlalchemy.orm import Session
from src.infra.sqlalchemy.models.user import User
from typing import Optional
from datetime import datetime
from src.infra.sqlalchemy.models.user_log import UserLog

class UserLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_log_with_user_data(self):
 
        results = self.db.query(
            UserLog.id.label("user_id"), 
            UserLog.log_time,
            User.name.label("user_name"), 
            User.image_path.label("user_image_path") 
        ).join(User, UserLog.user_id == User.id).all()


        formatted_results = []
        for row in results:
            formatted_results.append({
                "user_id": row.user_id,      
                "user_name": row.user_name,     
                "user_image_path": row.user_image_path 
            })
        return formatted_results

    def create(self, user_id: int, log_time: datetime):
        if isinstance(log_time, str):
            log_time = datetime.fromisoformat(log_time)

        new_log = UserLog(
        user_id=user_id,
        log_time=log_time
        )
        self.db.add(new_log)
        self.db.commit()
        self.db.refresh(new_log)
        return new_log
