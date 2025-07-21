from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
# Substitua pelas suas credenciais do MySQL
# Ex: mysql+mysqlconnector://user:password@homst/database_name
DATABASE_URL = "mysql+pymysql://root:Koraliny2406%40@localhost:3306/facialrecognition"

# Use variáveis de ambiente para manter flexível
MYSQL_USER = os.getenv("DB_USER", "usuario")
MYSQL_PASSWORD = os.getenv("DB_PASSWORD", "senha")
MYSQL_HOST = os.getenv("DB_HOST", "db")  # 'db' = nome do serviço MySQL no docker-compose
MYSQL_PORT = os.getenv("DB_PORT", "3306")
MYSQL_DB = os.getenv("DB_NAME", "projeto")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
