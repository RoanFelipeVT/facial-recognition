# Use a Python base image com ferramentas necessárias
FROM python:3.11-slim

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y \
    cmake \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos do seu repositório Git
COPY . .

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Expõe porta 3000 (API)
EXPOSE 3000

# --- COMANDO TEMPORÁRIO PARA MANUTENÇÃO ---
# Este comando mantém o contentor a funcionar sem fazer nada,
# permitindo-nos aceder ao terminal para executar o Alembic.
CMD ["tail", "-f", "/dev/null"]
