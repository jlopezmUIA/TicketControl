# Usa una imagen base de Python adecuada
FROM python:3.11.3-alpine3.18

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instala las dependencias del proyecto
RUN apk update \
    && apk add --no-cache gcc musl-dev postgresql-dev python3-dev libffi-dev \
    && pip install --upgrade pip

# Copia los archivos de requerimientos y el código fuente a la imagen
COPY ./requirements.txt ./

RUN pip install -r requirements.txt

COPY ./ ./

# Ejecuta el comando para iniciar el servidor Django
RUN ["python", "manage.py", "makemigrations"]
