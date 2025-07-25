from sqlalchemy import Column, Integer, String
from ..database import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))