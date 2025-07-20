from sqlalchemy.orm import Session
from src.infra.sqlalchemy.models.user import User, Admin
from src.schemas import schemas
from src.infra.sqlalchemy.security import verify_password

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, admin: schemas.AdminCreate):
      pass
    def authenticate(self, name: str, password: str):
        admin = self.db.query(Admin).filter(Admin.name == name).first()
        if not admin:
            return None
        if not verify_password(password, admin.hashed_password):
            return None
        return admin
