# 🐳 Definición de la Imagen Base
ARG AIRFLOW_VERSION=2.9.2
ARG PYTHON_VERSION=3.12
FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

# 🛠️ Configuración del Entorno
ENV AIRFLOW_HOME=/opt/airflow
WORKDIR ${AIRFLOW_HOME}

# 📦 Copia e Instalación de Dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 📁 Copia del Código del Proyecto