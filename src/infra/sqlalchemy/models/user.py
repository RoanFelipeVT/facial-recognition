from sqlalchemy import Column, Integer, String, Text
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    email = Column(String(255), unique=True, index=True)
    cellphone = Column(String(20), unique=True, index=True)
    position = Column(String(255), nullable=True)  # Posição do usuário, pode ser nulo
    image_path = Column(String(255)) # Caminho para a imagem salva
    encoding = Column(Text) # Armazenar como string JSON