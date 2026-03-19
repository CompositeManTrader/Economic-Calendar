# 🏛️ US Economic Calendar — Macro Research Dashboard

Dashboard de Streamlit para monitorear datos económicos de EE.UU. en tiempo real.

## Características

- **📅 Calendario económico** — Próximas publicaciones con fecha, hora, dato anterior y consenso estimado
- **📈 Gráficas históricas** — Series interactivas (Plotly) para 20+ indicadores
- **🏦 Monitor FOMC** — Calendario de reuniones y gráfica de Fed Funds Rate
- **🔬 Deep Dive** — Análisis detallado por indicador con estadísticas y distribución
- **🔀 Comparativos** — CPI vs Core PCE, desempleo vs inflación
- **⚡ Filtros** — Por categoría, impacto y rango temporal

## Deploy en Streamlit Cloud (Gratis)

### Paso 1: Crear repositorio en GitHub
1. Crea un repositorio nuevo en GitHub
2. Sube estos archivos manteniendo la estructura:
   ```
   tu-repo/
   ├── app.py
   ├── requirements.txt
   ├── .streamlit/
   │   └── config.toml
   └── README.md
   ```

### Paso 2: Conectar con Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Click en **"New app"**
4. Selecciona tu repositorio, branch `main`, y archivo `app.py`
5. Click en **"Deploy"**

### Paso 3: ¡Listo!
Tu app estará disponible en `https://tu-app.streamlit.app` en ~2 minutos.

## Datos

- **Fuente:** FRED (Federal Reserve Bank of St. Louis)
- **Costo:** $0 — No requiere API key
- **Actualización:** Automática al cargar (cache de 1 hora)
- **Consenso:** Estimación estadística basada en tendencia (media 3 periodos)

## Indicadores cubiertos

| Categoría | Indicadores |
|-----------|------------|
| Inflación | CPI, Core CPI, PCE, Core PCE, PPI |
| Empleo | NFP, Desempleo, Salarios, Jobless Claims, JOLTS |
| Actividad | PIB, Retail Sales, Producción Industrial |
| Confianza | U. Michigan Consumer Sentiment |
| Manufactura | Durable Goods Orders |
| Vivienda | Housing Starts, Existing Home Sales |
| Comercio | Trade Balance |
| Pol. Monetaria | Fed Funds Rate, Curva 10Y-2Y |

## Disclaimer

Este dashboard es una herramienta educativa y de investigación.
No constituye asesoría de inversión.
