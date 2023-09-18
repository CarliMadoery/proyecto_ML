# Usamos la imagen oficial de Python
FROM python:3.11-slim

# Establecemos el directorio de trabajo en /app
WORKDIR /app

# Copiamos el archivo de requerimientos (requirements.txt) a la imagen
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install -r requirements.txt

# Copiamos todo el contenido de la carpeta actual al directorio /app en la imagen
COPY . . 

# Exponemos el puerto 80 para la aplicación FastAPI
EXPOSE 80

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]