# Olist E-commerce Analytics API

Plataforma de procesamiento y análisis de datos diseñada para transformar registros transaccionales de Olist en insights estratégicos. El sistema combina una arquitectura robusta de backend con potentes visualizaciones de Business Intelligence.

---

## Visual Insights (Dashboard Preview)

El valor final del proyecto se materializa en dashboards interactivos que permiten la toma de decisiones basada en datos, como por ejemplo:

### **1. Segmentación de Clientes (Modelo RFM)**
Clasificación de usuarios según su Recencia, Frecuencia y Valor Monetario para identificar clientes fidelizados y aquellos en riesgo de abandono.
![Segmentación RFM](./assets/analysis_rfm_segmentation.png)

### **2. Retención y Cohortes**
Análisis del ciclo de vida del cliente para entender la recurrencia de compra a lo largo del tiempo.
![Análisis de Cohortes](./assets/analysis_cohort_retention.png)

### **3. Clasificación ABC de Categorías (Pareto)**
Segmentación del catálogo según su impacto en la facturación total. Aplica la Ley de Pareto para identificar el núcleo del negocio (Clase A), permitiendo priorizar esfuerzos logísticos y de marketing en las categorías que generan el 80% de los ingresos.
![Análisis de Categorías](./assets/analysis_category_abc_pareto.png)

---

## Arquitectura

El proyecto sigue un patrón de **arquitectura modular de tres capas**, asegurando escalabilidad y separación de responsabilidades:

1.  **Routes (API Layer):** Gestión de endpoints REST con **Flask**.
2.  **Services (Business Logic):** Procesamiento de datos y cálculos complejos con **Pandas** y **NumPy**.
3.  **Repositories (Data Access):** Consultas optimizadas en **SQL puro** (PostgreSQL) para garantizar eficiencia en la extracción.

> **Nota técnica:** Por optimización de almacenamiento en DB Cloud (límite 1GB), se omitió la tabla de geolocalización, delegando el análisis geográfico a las dimensiones presentes en las tablas de clientes y vendedores.

---

## Estructura clave del Proyecto

- `app/api/routes`: Endpoints de la API.
- `app/services`: Lógica de negocio y procesamiento con Pandas y NumPy.
- `app/repositories`: Consultas SQL puras.

---

## Instalación y Configuración

1. **Clonar el repositorio:**
`git clone ...`
2. **Crear e iniciar entorno virtual:** 
`python -m venv venv`
`source venv/scripts/activate` -> En Windows
3. **Instalar dependencias:** 
`pip install -r requirements.txt`
4. **Configurar variables de entorno:** 
Crea un archivo `.env` con las credenciales de PostgreSQL

---

## Base de Datos

Para inicializarla:

1. **Crear tablas:** `python -m scripts.init_db`
2. **Cargar datos:** `python -m scripts.ingest_data`

---

## Tecnologías

- **Backend:** Flask / Python
- **Base de Datos:** PostgreSQL
- **Análisis:** Pandas / Numpy
- **Visualización:** Power BI Desktop
