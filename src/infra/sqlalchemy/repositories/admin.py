from sqlalchemy.orm import Session
from ..models.admin import Admin # <--- CORRETO: Importa de 'sqlalchemy/models'
from ..schemas.admin import AdminCreate
from ..auth import get_password_hash # <--- CORRETO: Importa de 'sqlalchemy/auth'

class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_admin_by_name(self, name: str):
        return self.db.query(Admin).filter(Admin.name == name).first()

    def create_admin(self, admin: AdminCreate):
        hashed_password = get_password_hash(admin.password)
        db_admin = Admin(name=admin.name, hashed_password=hashed_password)
        self.db.add(db_admin)
        self.db.commit()
        self.db.refresh(db_admin)
        return db_admin