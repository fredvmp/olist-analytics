# Olist E-commerce Analytics API

Este proyecto es una plataforma de análisis de datos basada en el dataset de Olist, diseñada para extraer insights de negocio mediante una API REST y procesos de transformación de datos.

## Arquitectura
Por motivos de optimización de almacenamiento (límite de 1GB en DB Cloud), he decidido excluir la tabla `olist_geolocation_dataset.csv` ya que se pueden realizar análisis geográficos mediante las columnas de ciudad y estado presentes en las tablas de `customers` y `sellers`.

## Instalación y Configuración
1. **Clonar el repositorio:** `git clone ...`
2. **Crear entorno virtual:** `python -m venv venv`
3. **Instalar dependencias:** `pip install -r requirements.txt`
4. **Configurar variables de entorno:** Crea un archivo `.env` con las credenciales de PostgreSQL

## Base de Datos
Para inicializarla:
1. **Crear tablas:** `python -m scripts.init_db`
2. **Cargar datos:** `python -m scripts.ingest_data`

## Estructura clave del Proyecto
- `app/api/routes`: Endpoints de la API.
- `app/services`: Lógica de negocio y procesamiento con Pandas.
- `app/repositories`: Consultas SQL puras.

## Tecnologías
- **Backend:** Flask
- **Base de Datos:** PostgreSQL
- **Análisis:** Pandas / Numpy