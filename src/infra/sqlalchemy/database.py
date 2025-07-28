from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Substitua pelas suas credenciais do MySQL
# Ex: mysql+mysqlconnector://user:password@homst/database_name
DATABASE_URL = "mysql+pymysql://root:Koraliny2406%40@db:3306/facialrecognition"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
