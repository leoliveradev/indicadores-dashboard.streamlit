# Indicadores ENACOM — Dashboard

Dashboard profesional para la visualización de indicadores del sector de telecomunicaciones en Argentina, basado en los datos abiertos de **ENACOM**.
Este proyecto no es solo una visualización, sino una implementación robusta de Streamlit que sigue principios de **Clean Architecture** para garantizar escalabilidad y mantenimiento.

## 🛠️ Arquitectura y Estructura

El proyecto sigue un patrón de **dependencia descendente**: las capas superiores solo conocen a las que están debajo (`pages → components → services → config`).

```text
indicadores-dashboard/
├── app.py                # Punto de entrada y orquestación principal
├── config/               # Settings, constantes de columnas y diseño (Plotly theme)
├── services/             # Lógica de negocio: carga (cache), validación y transformaciones
├── components/           # UI Reutilizable: KPI cards, charts y filtros de sidebar
├── pages/                # Vistas por servicio (Internet, Móvil, TV, etc.)
└── data/                 # Datasets de ENACOM
```



## 🏗️ Principios de Diseño

**Una sola fuente de verdad por responsabilidad**:
- Nombres de archivos y columnas: Definidos centralizadamente en `config/constants.py`.
- Gestión de datos: Carga y lógica de caché optimizada en `services/data_manager.py`.
- Lógica de negocio: Transformaciones de Pandas mediante funciones puras en `services/transformers.py`.
- Identidad visual: Estilo de gráficos y paleta de colores en `config/theme.py`.

**Páginas livianas**: Cada página actúa únicamente como orquestador. El patrón de ejecución es siempre:
`load` → `validate` → `transform` → `render`.

## 🚀 Instalación y Ejecución
1.  Clonar el repositorio:
```bash
git clone [https://github.com/leoliveradev/indicadores-dashboard.streamlit.git](https://github.com/leoliveradev/indicadores-dashboard.streamlit.git)
cd indicadores-dashboard.streamlit
```
2. Instalar dependencias:
```bash
pip install -r requirements.txt
```
3. Ejecutar la aplicación:
```bash
streamlit run app.py
```

## ➕ Guía de Extensión

### Agregar una nueva página

1. Definir el nombre del nuevo archivo CSV `config/constants.py`.
2. Crear el archivo en `pages/N_NombreServicio.py`.
3. Importar las funciones necesarias de `services/` y `components/`.
*Nota: La página no debe contener lógica de manipulación de datos directa ni referencias explícitas a rutas de archivos.*

### Agregar un nuevo gráfico reutilizable
Añadir una función en `components/charts.py` siguiendo el patrón establecido:
-  Recibe un `DataFrame` y parámetros de configuración.
-  Aplica internamente `_apply_theme()` para mantener la coherencia visual.
-  Devuelve un objeto `figure` de Plotly listo para mostrar.

## 🔓 Fuente de Datos y Licencia

Los datos utilizados en esta API provienen del **[Portal de Datos Abiertos de ENACOM](https://datosabiertos.enacom.gob.ar/)** (Ente Nacional de Comunicaciones).

*   **Atribución:** Fuente: ENACOM.
*   **Licencia de los datos:** El contenido se distribuye bajo la licencia [Creative Commons Atribución 4.0 Internacional (CC BY 4.0)](https://creativecommons.org).
*   **Términos de uso:** El uso de esta información se rige por los [términos y condiciones generales](https://enacom.gob.ar) de ENACOM.
