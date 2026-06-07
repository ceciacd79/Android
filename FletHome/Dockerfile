FROM python:3.12
#Labels as key value pair
LABEL Maintainer="ceciacd.79"
LABEL version="1.0"
LABEL description="Flet dashboard with MQTT integration"
LABEL org.opencontainers.image.licenses="MIT"

# Configurazione OS
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apt-get update && apt-get install -y nano && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Copia i requirements dalla cartella specifica
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copia la cartella comune
COPY ./common /app/common

# 3. Copia il contenuto della cartella specifica dello script
COPY ./Flet /app

# 4. Imposta PYTHONPATH così Python trova i moduli in /app/common
ENV PYTHONPATH=/app

CMD ["python", "main.py"]