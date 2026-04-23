# Indicadores ENACOM — Dashboard

Dashboard profesional para la visualización y análisis de indicadores del sector de telecomunicaciones en Argentina.

## 🚀 Arquitectura del Sistema

El dashboard funciona como un cliente de datos que se conecta a una infraestructura moderna:
* **Fuente de Datos:** Portal de Datos Abiertos de ENACOM.
* **Backend:** API desarrollada en TypeScript/Node.js.
* **Base de Datos:** PostgreSQL administrado en **Supabase**.
* **Frontend:** Streamlit Cloud.

## 📁 Estructura del proyecto

```text
dashboard/
├── app.py                  # Punto de entrada (Entry point)
├── requirements.txt        # Dependencias del proyecto
├── .streamlit/
│   └── secrets.toml        # Configuración local de variables de entorno (no trackeado)
├── config/
│   ├── settings.py         # Configuración global (API URLs, Timeouts)
│   ├── theme.py            # Estilos visuales y paleta de colores de Plotly
│   ├── constants.py        # Constantes globales (Provincias, Nombres de columnas)
│   └── endpoints/          # Definición de recursos de la API
│       ├── __init__.py     # Exportación centralizada de servicios
│       ├── internet.py     # Endpoints de conectividad fija
│       ├── movil.py        # Endpoints de telefonía móvil
│       └── ...             # Otros servicios (TV, Postal, Telefonia)
├── services/
│   ├── data_manager.py     # Motor de carga, cache (st.cache_data) y normalización
│   ├── data_validator.py   # Validación de integridad de datos
│   └── transformers.py     # Lógica de negocio y transformaciones de Pandas
├── components/             # UI Reutilizable (Charts, KPI cards, Filters)
└── pages/                  # Vistas del dashboard (Internet, Móvil, TV, etc.)

## 🛠️ Instalación y Configuración

1. Clonar el repositorio
```bash
git clone https://github.com/leoliveradev/indicadores-dashboard.streamlit
cd indicadores-dashboard.streamlit
```

2. Instalar dependencias
```bash
pip install -r requirements.txt
```

3. Configurar Variables de Entorno
Crea un archivo llamado `.streamlit/secrets.toml` en la raíz del proyecto para conectar con la API:

4. Ejecutar localmente
```bash
streamlit run app.py
```

## 🏗️ Principios de Diseño

**Dependencia descendente**: las capas solo conocen a la que está debajo.
`pages → components → services → config`.

**Una sola fuente de verdad por responsabilidad**:
- Nombres de archivos → `config/constants.py`
- Carga y cache → `services/data_manager.py`
- Lógica de pandas → `services/transformers.py`
- Colores y estilo → `config/theme.py`

**Páginas livianas**: Cada página solo orquesta.
El patrón es siempre: `load → validate → transform → render`.

**Consumo Eficiente**: Se implementa un sistema de cacheo inteligente con un TTL (Time To Live) de 1 hora para minimizar el tráfico hacia la API y mejorar la experiencia de usuario.

**Normalización Automática**: El DataManager procesa cada respuesta de la API para estandarizar nombres de columnas (snake_case), limpiar strings y asegurar tipos de datos numéricos.

## 📈 Cómo extender el Dashboard

### Agregar un nuevo endpoint:

1. Define el string del recurso en su archivo correspondiente dentro de `config/endpoints/`.
2. Si es un servicio nuevo, asegúrate de exportar la clase en `config/endpoints/__init__.py`.

### Crear una nueva página:

1. Crea el archivo en `pages/`.
2. Usa el patrón estándar:

```bash
df = DataManager.load(InternetEndpoints.NUEVO_RECURSO)
# El DataFrame ya viene normalizado y cacheado.
```

### Agregar un nuevo gráfico reutilizable

Agregar una función en `components/charts.py` siguiendo el patrón existente:
recibe un DataFrame y parámetros, aplica `_apply_theme()`, devuelve una figura Plotly.

## 📄 Licencia
Este proyecto es de código abierto y utiliza datos públicos. Consulta los términos de uso en ENACOM Datos Abiertos.