from fastapi import FastAPI
from src.infra.sqlalchemy.database import Base, engine
from src.infra.sqlalchemy.routes import admin, user, recognition, user_log

app = FastAPI(
    title="API de Reconhecimento Facial",
    description="Backend para gerenciamento de usuários e reconhecimento facial com autenticação JWT para administradores."
)


Base.metadata.create_all(bind=engine)

# Inclui as rotas
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(user_log.router)
app.include_router(recognition.router) 

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Reconhecimento Facial!"}