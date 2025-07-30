from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.infra.sqlalchemy.database import engine, Base
from src.services.user_service import router as user_router
from src.services.admin_service import router as admin_router
from src.services.user_log_service import router as user_log_router

# Cria as tabelas no banco de dados (se não existirem)
# NOTA: É melhor usar Alembic para isto, mas para garantir que funciona, mantemos aqui.
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configuração do CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas da API
app.include_router(user_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(user_log_router, prefix="/api")

# --- NOVO CÓDIGO PARA SERVIR O FRONTEND ---
# Monta a pasta 'static' (que contém o nosso site Next.js) na raiz.
# O FastAPI irá agora procurar por um 'index.html' e servir o seu site.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
