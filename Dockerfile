# --- Dockerfile Multi-Estágio para Aplicação Completa (Frontend + Backend) ---

# --- ESTÁGIO 1: Construir o Frontend (Next.js) ---
# Usamos uma imagem Node.js para construir o nosso site.
FROM node:18-slim AS builder

# Define o diretório de trabalho
WORKDIR /app

# Copia os ficheiros de configuração do frontend
COPY package*.json ./
COPY next.config.js ./
COPY tailwind.config.ts ./
COPY tsconfig.json ./
COPY public ./public
COPY src/app ./src/app
COPY src/components ./src/components
COPY src/styles ./src/styles

# Instala as dependências do frontend
RUN npm install

# Constrói o frontend para produção. Isto cria uma pasta 'out' com o site estático.
RUN npm run build


# --- ESTÁGIO 2: Configurar o Backend (Python) e Servir o Frontend ---
# Começamos com a nossa imagem Python original.
FROM python:3.11-slim

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho
WORKDIR /app

# Copia os ficheiros do backend
COPY requirements.txt .
COPY alembic.ini .
COPY alembic ./alembic
COPY src/infra ./src/infra
COPY src/schemas ./src/schemas
COPY src/services ./src/services
COPY main.py .

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copia o site estático que foi construído no Estágio 1 para uma pasta 'static'
COPY --from=builder /app/out ./static

# Expõe a porta 3000
EXPOSE 3000

# Comando para iniciar o FastAPI com uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
