# Usa una imagen base oficial de Python
FROM python:3.11

# Establece el directorio de trabajo en el contenedor
WORKDIR /opt/

# Configura variables de entorno para Celery
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt /opt/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código fuente de la aplicación al contenedor
COPY . /opt/