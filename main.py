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

origins = [
    "https://nick-frontend-app.zxwnxt.easypanel.host",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("images"):
    os.makedirs("images")

# Servir a pasta de imagens como arquivos estáticos
app.mount("/images", StaticFiles(directory="images"), name="images")

app.include_router(admin.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(user_log.router, prefix="/api")
app.include_router(recognition.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Reconhecimento Facial!"}
