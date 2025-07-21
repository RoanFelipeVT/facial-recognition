# Usa uma imagem Python com ferramentas de build C++ já instaladas
FROM python:3.10-slim

# Instala dependências do sistema (build-essential, cmake, libgl1, libglib2.0-0)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia seus arquivos de código
COPY . .

# Instala dependências do Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install -r installed_packages.txt

# Exponha a porta
EXPOSE 3000

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
