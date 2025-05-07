# Usa una imagen base de Python
FROM python:3.9

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos de requisitos
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Expón el puerto en el que correrá Uvicorn
EXPOSE 8000

# Comando para correr FastAPI con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
