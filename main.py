from fastapi import FastAPI
from src.infra.sqlalchemy.database import Base, engine
from src.infra.sqlalchemy.routes import admin, user, recognition

app = FastAPI(
    title="API de Reconhecimento Facial",
    description="Backend para gerenciamento de usuários e reconhecimento facial com autenticação JWT para administradores."
)

""" Cria as tabelas no banco de dados, só deve ser chamada na inicialização do banco
 Se estiver usando um banco de dados existente, comente a linha abaixo para evitar recriação
"""
# Base.metadata.create_all(bind=engine)

# Inclui as rotas
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(recognition.router) 

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Reconhecimento Facial!"}