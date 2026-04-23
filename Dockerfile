# Usamos una imagen de Python ligera
FROM python:3.11-slim

# Directorio de trabajo dentro del servidor
WORKDIR /app

# Copiamos e instalamos las librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el proyecto (incluyendo los CSV optimizados)
COPY . .

# Exponemos el puerto 7860 que es el que usa Hugging Face
EXPOSE 7860

# Comando para arrancar la app con gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "proyectoclima:server"]