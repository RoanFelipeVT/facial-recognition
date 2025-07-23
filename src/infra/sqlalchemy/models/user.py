from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    cellphone = Column(String(20), unique=True, index=True)
    image_path = Column(String(255)) # Caminho para a imagem salva
    encoding = Column(Text) # Armazenar como string JSON

    logs = relationship("UserLog", back_populates="user")
