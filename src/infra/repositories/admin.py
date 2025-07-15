from sqlalchemy.orm import Session
from src.infra.sqlalchemy.models.admin import Admin
from passlib.context import CryptContext
from fastapi import HTTPException, status

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str):
        return self.db.query(Admin).filter(Admin.name == name).first()

    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password: str):
        return pwd_context.hash(password)

    def create(self, name: str, password: str):
        admin_exist = self.get_by_name(name)
        if admin_exist:
            raise HTTPException(status_code=400, detail="Admin já existe")
        hashed_password = self.hash_password(password)
        admin = Admin(name=name, hashed_password=hashed_password)
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        return admin
