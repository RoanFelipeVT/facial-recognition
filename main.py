from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from src.infra.sqlalchemy.database import Base, engine
from src.infra.sqlalchemy.routes import admin, user, recognition, user_log

app = FastAPI(
    title="API de Reconhecimento Facial",
    description="Backend para gerenciamento de usuários e reconhecimento facial com autenticação JWT para administradores."
)

# Permitir frontend
origins = [
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Garantir que pasta de imagens exista
if not os.path.exists("images"):
    os.makedirs("images")

# Expor imagens publicamente
app.mount("/images", StaticFiles(directory="images"), name="images")

# Criar tabelas do banco
Base.metadata.create_all(bind=engine)

# Inclui as rotas
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(user_log.router)
app.include_router(recognition.router) 

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Reconhecimento Facial!"}
