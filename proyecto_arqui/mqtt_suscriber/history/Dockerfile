# Usa una imagen base de Python
FROM python:3.11-slim

# Instalar curl y ping
RUN apt-get update && apt-get install -y curl iputils-ping

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos y el código fuente
COPY requirements.txt .
COPY mqtt_subscriber_history.py .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando para ejecutar el suscriptor MQTT
CMD ["python3", "-u", "mqtt_subscriber_history.py"]
