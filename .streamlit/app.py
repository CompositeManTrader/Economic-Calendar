"""
🏛️ US Economic Calendar — Macro Research Dashboard
====================================================
Streamlit app for monitoring US economic data releases.
Style: J.P. Morgan Global Economics Research

Deploy: Streamlit Community Cloud (free)
    1. Push this repo to GitHub
    2. Go to share.streamlit.io
    3. Connect your repo → Deploy

Author: Macro Research Desk
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import calendar
import requests
import time

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="US Economic Calendar",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS — JPM-inspired dark nav + clean body
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;1,9..40,400&family=JetBrains+Mono:wght@400;600&display=swap');

    /* Global */
    .stApp {
        font-family: 'DM Sans', sans-serif;
    }

    /* Main header area */
    .main-header {
        background: linear-gradient(135deg, #0a0f1a 0%, #141e30 50%, #1a2740 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .main-header h1 {
        color: #e8ecf1;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #7a8ba3;
        font-size: 0.9rem;
        margin: 0.3rem 0 0 0;
    }
    .main-header .live-badge {
        display: inline-block;
        background: #00c853;
        color: #0a0f1a;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        margin-left: 12px;
        letter-spacing: 0.5px;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    /* KPI cards */
    .kpi-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0 1.5rem 0;
        flex-wrap: wrap;
    }
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e5e9f0;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        flex: 1;
        min-width: 180px;
        transition: transform 0.15s, box-shadow 0.15s;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0a0f1a;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.75rem;
        color: #7a8ba3;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 500;
        margin-top: 4px;
    }
    .kpi-delta-up { color: #00c853; font-size: 0.85rem; font-weight: 600; }
    .kpi-delta-down { color: #ff1744; font-size: 0.85rem; font-weight: 600; }
    .kpi-delta-neutral { color: #7a8ba3; font-size: 0.85rem; }

    /* Calendar table */
    .cal-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.85rem;
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #e5e9f0;
    }
    .cal-table thead {
        background: #0a0f1a;
    }
    .cal-table th {
        color: #c5cdd8;
        padding: 12px 16px;
        text-align: left;
        font-weight: 600;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }
    .cal-table td {
        padding: 11px 16px;
        border-bottom: 1px solid #f0f2f5;
        color: #2c3e50;
    }
    .cal-table tr:hover td {
        background: #f7f9fc;
    }
    .cal-table tr:last-child td {
        border-bottom: none;
    }

    /* Impact badges */
    .badge-high {
        background: #fff0f0;
        color: #d32f2f;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.72rem;
        letter-spacing: 0.3px;
    }
    .badge-med {
        background: #fff8e1;
        color: #e65100;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.72rem;
    }
    .badge-low {
        background: #f1f8e9;
        color: #558b2f;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.72rem;
    }

    /* Countdown chips */
    .countdown {
        background: #e3f2fd;
        color: #1565c0;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }
    .countdown-urgent {
        background: #fce4ec;
        color: #c62828;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        animation: pulse 1.5s infinite;
    }
    .countdown-today {
        background: #c62828;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Section headers */
    .section-header {
        border-left: 4px solid #0a0f1a;
        padding-left: 14px;
        margin: 2rem 0 1rem 0;
    }
    .section-header h2 {
        color: #0a0f1a;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0;
    }
    .section-header p {
        color: #7a8ba3;
        font-size: 0.82rem;
        margin: 2px 0 0 0;
    }

    /* FOMC row highlight */
    .fomc-soon { background: #fffde7 !important; }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: #f7f9fc;
    }

    /* Hide default streamlit padding */
    .block-container {
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# INDICADORES CATALOG
# ============================================================
INDICADORES = [
    # INFLACIÓN
    {'fred_id': 'CPIAUCSL', 'nombre': 'CPI — Consumer Price Index', 'nombre_corto': 'CPI',
     'categoria': 'Inflación', 'cat_icon': '🔥', 'frecuencia': 'Mensual', 'impacto': 'ALTO',
     'fuente': 'BLS', 'unidad': 'Índice', 'descripcion': 'Variación de precios al consumidor. El indicador de inflación más seguido.', 'transform': 'pct_change_12'},
    {'fred_id': 'CPILFESL', 'nombre': 'Core CPI (Ex-Food & Energy)', 'nombre_corto': 'Core CPI',
     'categoria': 'Inflación', 'cat_icon': '🔥', 'frecuencia': 'Mensual', 'impacto': 'ALTO',
     'fuente': 'BLS', 'unidad': 'Índice', 'descripcion': 'CPI excluyendo alimentos y energía.', 'transform': 'pct_change_12'},
    {'fred_id': 'PCEPI', 'nombre': 'PCE Price Index', 'nombre_corto': 'PCE',
     'categoria': 'Inflación', 'cat_icon': '🔥', 'frecuencia': 'Mensual', 'impacto': 'ALTO',
     'fuente': 'BEA', 'unidad': 'Índice', 'descripcion': 'Indicador de inflación PREFERIDO de la Fed. Meta: 2%.', 'transform': 'pct_change_12'},
    {'fred_id': 'PCEPILFE', 'nombre': 'Core PCE (Ex-Food & Energy)', 'nombre_corto': 'Core PCE',
     'categoria': 'Inflación', 'cat_icon': '🔥', 'frecuencia': 'Mensual', 'impacto': 'ALTO',
     'fuente': 'BEA', 'unidad': 'Índice', 'descripcion': 'La métrica que la Fed usa para su objetivo de inflación del 2%.', 'transform': 'pct_change_12'},
    {'fred_id': 'PPIFIS', 'nombre': 'PPI — Producer Price Index', 'nombre_corto': 'PPI',
     'categoria': 'Inflación', 'cat_icon': '🔥', 'frecuencia': 'Mensual', 'impacto': 'MEDIO',
     'fuente': 'BLS', 'unidad': 'Índice', 'descripcion': 'Precios a nivel productor. Indicador adelantado de inflación.', 'transform': 'pct_change_12'},

    # EMPLEO
    {'fred_id': 'PAYEMS', 'nombre': 'Nonfarm Payrolls (NFP)', 'nombre_corto': 'NFP',
     'categoria': 'Empleo', 'cat_icon': '👷', 'frecuencia': 'Mensual', 'impacto': 'ALTO',
     'fuente': 'BLS', 'unidad': 'K personas', 'descripcion': 'Cambio mensual en empleo no agrícola. Mueve mercados.', 'transform': 'diff'},
    {'fred_id': 'UNRATE', 'nombre': 'Unemployment Rate', 'nombre_corto': 'Desempleo',
     'categoria': 'Empleo', 'cat_icon': '👷', 'frecuencia': 'Mensual', 'impacto': 'ALTO',
     'fuente': 'BLS', 'unidad': '%', 'descripcion': 'Tasa de desempleo. Parte del mandato dual de la Fed.', 'transform': 'level'},
    {'fred_id': 'CES0500000003', 'nombre': 'Average Hourly Earnings', 'nombre_corto': 'Salarios/Hora',
     'categoria': 'Empleo', 'cat_icon': '👷', 'frecuencia': 'Mensual', 'impacto': 'ALTO',
     'fuente': 'BLS', 'unidad': 'USD/hr', 'descripcion': 'Salario promedio por hora. Presiones inflacionarias laborales.', 'transform': 'pct_change_12'},
    {'fred_id': 'ICSA', 'nombre': 'Initial Jobless Claims', 'nombre_corto': 'Jobless Claims',
     'categoria': 'Empleo', 'cat_icon': '👷', 'frecuencia': 'Semanal', 'impacto': 'MEDIO',
     'fuente': 'DOL', 'unidad': 'Personas', 'descripcion': 'Solicitudes semanales de seguro de desempleo.', 'transform': 'level'},
    {'fred_id': 'JTSJOL', 'nombre': 'JOLTS — Job Openings', 'nombre_corto': 'JOLTS',
     'categoria': 'Empleo', 'cat_icon': '👷', 'frecuencia': 'Mensual', 'impacto': 'MEDIO',
     'fuente': 'BLS', 'unidad': 'K vacantes', 'descripcion': 'Vacantes laborales. La Fed lo monitorea de cerca.', 'transform': 'level'},

    # ACTIVIDAD / PIB
    {'fred_id': 'GDP', 'nombre': 'GDP — Gross Domestic Product', 'nombre_corto': 'PIB',
     'categoria': 'Actividad / PIB', 'cat_icon': '📈', 'frecuencia': 'Trimestral', 'impacto': 'ALTO',
     'fuente': 'BEA', 'unidad': 'Bn USD', 'descripcion': 'Producto Interno Bruto.', 'transform': 'pct_change_annualized'},
    {'fred_id': 'RSAFS', 'nombre': 'Retail Sales (Advance)', 'nombre_corto': 'Retail Sales',
     'categoria': 'Actividad / PIB', 'cat_icon': '📈', 'frecuencia': 'Mensual', 'impacto': 'ALTO',
     'fuente': 'Census', 'unidad': 'Mn USD', 'descripcion': 'Ventas al por menor. Consumo = ~70% del PIB.', 'transform': 'pct_change'},
    {'fred_id': 'INDPRO', 'nombre': 'Industrial Production', 'nombre_corto': 'Prod. Industrial',
     'categoria': 'Actividad / PIB', 'cat_icon': '📈', 'frecuencia': 'Mensual', 'impacto': 'MEDIO',
     'fuente': 'Fed Board', 'unidad': 'Índice', 'descripcion': 'Producción industrial de fábricas, minas y utilidades.', 'transform': 'pct_change'},

    # CONFIANZA
    {'fred_id': 'UMCSENT', 'nombre': 'U. Michigan Consumer Sentiment', 'nombre_corto': 'UMich Sentiment',
     'categoria': 'Confianza', 'cat_icon': '🧠', 'frecuencia': 'Mensual', 'impacto': 'MEDIO',
     'fuente': 'U. Michigan', 'unidad': 'Índice', 'descripcion': 'Confianza del consumidor. Incluye expectativas de inflación.', 'transform': 'level'},

    # MANUFACTURA
    {'fred_id': 'DGORDER', 'nombre': 'Durable Goods Orders', 'nombre_corto': 'Durable Goods',
     'categoria': 'Manufactura', 'cat_icon': '🏭', 'frecuencia': 'Mensual', 'impacto': 'MEDIO',
     'fuente': 'Census', 'unidad': 'Mn USD', 'descripcion': 'Pedidos de bienes duraderos. Indicador de inversión.', 'transform': 'pct_change'},

    # VIVIENDA
    {'fred_id': 'HOUST', 'nombre': 'Housing Starts', 'nombre_corto': 'Housing Starts',
     'categoria': 'Vivienda', 'cat_icon': '🏠', 'frecuencia': 'Mensual', 'impacto': 'MEDIO',
     'fuente': 'Census', 'unidad': 'K unidades', 'descripcion': 'Inicio de construcción de viviendas.', 'transform': 'level'},
    {'fred_id': 'EXHOSLUSM495S', 'nombre': 'Existing Home Sales', 'nombre_corto': 'Existing Home Sales',
     'categoria': 'Vivienda', 'cat_icon': '🏠', 'frecuencia': 'Mensual', 'impacto': 'MEDIO',
     'fuente': 'NAR', 'unidad': 'K unidades', 'descripcion': 'Ventas de casas existentes.', 'transform': 'level'},

    # COMERCIO
    {'fred_id': 'BOPGSTB', 'nombre': 'Trade Balance', 'nombre_corto': 'Trade Balance',
     'categoria': 'Comercio', 'cat_icon': '🌍', 'frecuencia': 'Mensual', 'impacto': 'MEDIO',
     'fuente': 'Census/BEA', 'unidad': 'Mn USD', 'descripcion': 'Exportaciones menos importaciones.', 'transform': 'level'},

    # POLÍTICA MONETARIA
    {'fred_id': 'FEDFUNDS', 'nombre': 'Federal Funds Rate', 'nombre_corto': 'Fed Funds Rate',
     'categoria': 'Política Monetaria', 'cat_icon': '🏦', 'frecuencia': 'Diario', 'impacto': 'ALTO',
     'fuente': 'Federal Reserve', 'unidad': '%', 'descripcion': 'Tasa de referencia de la Fed.', 'transform': 'level'},
    {'fred_id': 'T10Y2Y', 'nombre': 'Yield Spread 10Y-2Y', 'nombre_corto': 'Curva 10Y-2Y',
     'categoria': 'Política Monetaria', 'cat_icon': '🏦', 'frecuencia': 'Diario', 'impacto': 'ALTO',
     'fuente': 'Treasury/Fed', 'unidad': '%', 'descripcion': 'Spread 10Y-2Y. Inversión = señal de recesión.', 'transform': 'level'},
]

# JPM Color palette
C = {
    'bg_dark': '#0a0f1a',
    'navy': '#141e30',
    'text_primary': '#0a0f1a',
    'text_secondary': '#7a8ba3',
    'accent': '#1565c0',
    'green': '#00c853',
    'red': '#ff1744',
    'gold': '#ffab00',
    'grid': '#f0f2f5',
    'line1': '#0a0f1a',
    'line2': '#1565c0',
    'line3': '#ff6d00',
    'line4': '#00bfa5',
}


# ============================================================
# DATA FETCHING (cached)
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fred_data(fred_id, start='2015-01-01'):
    """Fetch series from FRED public CSV endpoint (no API key needed)."""
    try:
        url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={fred_id}&cosd={start}'
        df = pd.read_csv(url, parse_dates=['DATE'], index_col='DATE')
        col = df.columns[0]
        df[col] = pd.to_numeric(df[col], errors='coerce')
        return df[col].dropna()
    except Exception:
        return None


def apply_transform(data, transform):
    """Apply the appropriate transformation to a FRED series."""
    if data is None or len(data) < 2:
        return None, ''
    if transform == 'pct_change_12' and len(data) > 12:
        return (data.pct_change(periods=12) * 100).dropna(), '% YoY'
    elif transform == 'pct_change':
        return (data.pct_change() * 100).dropna(), '% MoM'
    elif transform == 'pct_change_annualized':
        return (data.pct_change() * 400).dropna(), '% SAAR'
    elif transform == 'diff':
        return data.diff().dropna(), 'Cambio (K)'
    else:
        return data, 'Nivel'


# ============================================================
# CALENDAR BUILDER
# ============================================================
RELEASE_SCHEDULE = [
    ('Nonfarm Payrolls', 'PAYEMS', 'first_friday', '08:30', 'ALTO'),
    ('Unemployment Rate', 'UNRATE', 'first_friday', '08:30', 'ALTO'),
    ('Avg. Hourly Earnings', 'CES0500000003', 'first_friday', '08:30', 'ALTO'),
    ('CPI (All Items)', 'CPIAUCSL', 'mid_12', '08:30', 'ALTO'),
    ('Core CPI', 'CPILFESL', 'mid_12', '08:30', 'ALTO'),
    ('PPI (Final Demand)', 'PPIFIS', 'mid_14', '08:30', 'MEDIO'),
    ('Retail Sales', 'RSAFS', 'mid_15', '08:30', 'ALTO'),
    ('PCE Price Index', 'PCEPI', 'late_28', '08:30', 'ALTO'),
    ('Core PCE', 'PCEPILFE', 'late_28', '08:30', 'ALTO'),
    ('Industrial Production', 'INDPRO', 'mid_16', '09:15', 'MEDIO'),
    ('Housing Starts', 'HOUST', 'mid_18', '08:30', 'MEDIO'),
    ('Durable Goods', 'DGORDER', 'late_26', '08:30', 'MEDIO'),
    ('Consumer Sentiment', 'UMCSENT', 'mid_14', '10:00', 'MEDIO'),
    ('JOLTS Job Openings', 'JTSJOL', 'first_7', '10:00', 'MEDIO'),
    ('Trade Balance', 'BOPGSTB', 'first_6', '08:30', 'MEDIO'),
    ('Initial Claims', 'ICSA', 'every_thursday', '08:30', 'MEDIO'),
]


def estimate_next_release(schedule_type, today, months_ahead=3):
    """Estimate next release date based on publication pattern."""
    def gen_months():
        dates = []
        y, m = today.year, today.month
        for _ in range(months_ahead):
            dates.append((y, m))
            m += 1
            if m > 12:
                m = 1
                y += 1
        return dates

    if schedule_type == 'first_friday':
        for y, m in gen_months():
            cal = calendar.monthcalendar(y, m)
            for week in cal:
                if week[calendar.FRIDAY] != 0:
                    d = datetime(y, m, week[calendar.FRIDAY])
                    if d.date() >= today.date():
                        return d
                    break

    elif schedule_type == 'every_thursday':
        d = today
        while d.weekday() != 3:
            d += timedelta(days=1)
        return d

    elif schedule_type.startswith('mid_'):
        target = int(schedule_type.split('_')[1])
        for y, m in gen_months():
            max_d = calendar.monthrange(y, m)[1]
            d = datetime(y, m, min(target, max_d))
            while d.weekday() >= 5:
                d += timedelta(days=1)
            if d.date() >= today.date():
                return d

    elif schedule_type.startswith('late_'):
        target = int(schedule_type.split('_')[1])
        for y, m in gen_months():
            max_d = calendar.monthrange(y, m)[1]
            d = datetime(y, m, min(target, max_d))
            while d.weekday() >= 5:
                d += timedelta(days=1)
            if d.date() >= today.date():
                return d

    elif schedule_type.startswith('first_'):
        target = int(schedule_type.split('_')[1])
        for y, m in gen_months():
            d = datetime(y, m, min(target, calendar.monthrange(y, m)[1]))
            while d.weekday() >= 5:
                d += timedelta(days=1)
            if d.date() >= today.date():
                return d

    return None


@st.cache_data(ttl=3600, show_spinner=False)
def build_calendar(days_ahead=60):
    """Build the full economic calendar with previous values and consensus."""
    today = datetime.now()
    events = []

    for nombre, fred_id, sched, hora, impacto in RELEASE_SCHEDULE:
        next_date = estimate_next_release(sched, today)
        if next_date and (next_date - today).days <= days_ahead:
            # Get previous value
            data = fetch_fred_data(fred_id, start='2020-01-01')
            ind = next((i for i in INDICADORES if i['fred_id'] == fred_id), None)
            prev_str, cons_str = 'N/A', 'N/A'

            if data is not None and len(data) > 1 and ind:
                transformed, unit = apply_transform(data, ind['transform'])
                if transformed is not None and len(transformed) > 3:
                    last = transformed.iloc[-1]
                    avg3 = transformed.iloc[-3:].mean()

                    if ind['transform'] == 'diff':
                        prev_str = f"{last:+,.0f}"
                        cons_str = f"{avg3:+,.0f}"
                    elif 'pct' in ind['transform']:
                        prev_str = f"{last:.2f}%"
                        cons_str = f"{avg3:.2f}%"
                    else:
                        prev_str = f"{last:,.1f}"
                        cons_str = f"{avg3:,.1f}"

            days_until = (next_date - today).days
            events.append({
                'date': next_date,
                'date_str': next_date.strftime('%a %b %d'),
                'time': hora,
                'event': nombre,
                'fred_id': fred_id,
                'impact': impacto,
                'previous': prev_str,
                'consensus': cons_str,
                'days_until': days_until,
            })

    events.sort(key=lambda x: x['date'])
    return events


# ============================================================
# FOMC CALENDAR
# ============================================================
FOMC_MEETINGS = [
    ('2025-01-29', False), ('2025-03-19', True), ('2025-05-07', False),
    ('2025-06-18', True), ('2025-07-30', False), ('2025-09-17', True),
    ('2025-10-29', False), ('2025-12-10', True),
    ('2026-01-28', False), ('2026-03-18', True), ('2026-05-06', False),
    ('2026-06-17', True), ('2026-07-29', False), ('2026-09-16', True),
    ('2026-10-28', False), ('2026-12-09', True),
]


def get_upcoming_fomc():
    today = datetime.now().date()
    upcoming = []
    for date_str, has_sep in FOMC_MEETINGS:
        d = datetime.strptime(date_str, '%Y-%m-%d').date()
        if d >= today:
            upcoming.append({
                'date': d.strftime('%b %d, %Y'),
                'type': 'Regular + SEP' if has_sep else 'Regular',
                'dot_plot': '✅' if has_sep else '—',
                'days': (d - today).days,
            })
    return upcoming


# ============================================================
# CHART BUILDER
# ============================================================
def create_chart(indicator, height=420):
    """Create a professional Plotly chart for an indicator."""
    data = fetch_fred_data(indicator['fred_id'], start='2015-01-01')
    if data is None:
        return None

    transformed, unit = apply_transform(data, indicator['transform'])
    if transformed is None or len(transformed) < 5:
        return None

    fig = go.Figure()

    # Main series
    fig.add_trace(go.Scatter(
        x=transformed.index, y=transformed.values,
        mode='lines', name=indicator['nombre_corto'],
        line=dict(color=C['line1'], width=2.2),
        hovertemplate='%{x|%b %d, %Y}<br><b>%{y:.2f}</b><extra></extra>'
    ))

    # 6-period moving average
    if len(transformed) > 6:
        ma = transformed.rolling(6).mean()
        fig.add_trace(go.Scatter(
            x=ma.index, y=ma.values,
            mode='lines', name='MA-6',
            line=dict(color=C['gold'], width=1.5, dash='dash'),
            opacity=0.75,
            hovertemplate='MA-6: %{y:.2f}<extra></extra>'
        ))

    # Last value marker
    last_val = transformed.iloc[-1]
    last_date = transformed.index[-1]
    fig.add_trace(go.Scatter(
        x=[last_date], y=[last_val],
        mode='markers+text', showlegend=False,
        marker=dict(color=C['red'], size=9),
        text=[f'  {last_val:.2f}'], textposition='middle right',
        textfont=dict(size=12, color=C['red'], family='JetBrains Mono, monospace'),
        hoverinfo='skip'
    ))

    # Fed target for inflation indicators
    if indicator['categoria'] == 'Inflación' and 'pct' in indicator['transform']:
        fig.add_hline(y=2.0, line_dash='dot', line_color=C['green'], line_width=1.5,
                      annotation_text='Fed Target 2%', annotation_position='bottom right',
                      annotation_font=dict(color=C['green'], size=11))

    # COVID recession
    if pd.Timestamp('2020-02-01') >= transformed.index.min():
        fig.add_vrect(x0='2020-02-01', x1='2020-04-01',
                      fillcolor='rgba(255,23,68,0.08)', layer='below', line_width=0)

    fig.update_layout(
        title=dict(
            text=f"<b>{indicator['nombre']}</b><br>"
                 f"<span style='font-size:11px;color:{C['text_secondary']}'>"
                 f"{indicator['fuente']} · {indicator['frecuencia']} · "
                 f"Último: {last_val:.2f} {unit} ({last_date.strftime('%b %d, %Y')})</span>",
            x=0.01, font=dict(size=14, family='DM Sans')
        ),
        xaxis=dict(
            showgrid=False,
            rangeselector=dict(
                buttons=[
                    dict(count=1, label='1Y', step='year', stepmode='backward'),
                    dict(count=3, label='3Y', step='year', stepmode='backward'),
                    dict(count=5, label='5Y', step='year', stepmode='backward'),
                    dict(step='all', label='All')
                ],
                bgcolor='#f0f2f5', activecolor=C['bg_dark'],
                font=dict(color='#333', size=11)
            )
        ),
        yaxis=dict(showgrid=True, gridcolor=C['grid'], title=unit, zeroline=True, zerolinecolor='#ddd'),
        plot_bgcolor='white', paper_bgcolor='white',
        height=height,
        margin=dict(l=55, r=25, t=80, b=45),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=11)),
        hovermode='x unified'
    )
    return fig


def create_multi_chart(indicators, title, height=420):
    """Create a multi-indicator comparison chart."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    colors = [C['line1'], C['red'], C['line4'], C['line3']]

    for i, ind in enumerate(indicators):
        data = fetch_fred_data(ind['fred_id'], start='2015-01-01')
        if data is not None:
            transformed, unit = apply_transform(data, ind['transform'])
            if transformed is not None:
                fig.add_trace(go.Scatter(
                    x=transformed.index, y=transformed.values,
                    mode='lines', name=f"{ind['nombre_corto']} ({unit})",
                    line=dict(color=colors[i % len(colors)], width=2),
                    hovertemplate=f"{ind['nombre_corto']}: " + '%{y:.2f}<extra></extra>'
                ), secondary_y=(i >= 1 and len(indicators) == 2))

    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", x=0.01, font=dict(size=14, family='DM Sans')),
        plot_bgcolor='white', paper_bgcolor='white',
        height=height, hovermode='x unified',
        legend=dict(orientation='h', y=1.1, font=dict(size=11)),
        margin=dict(l=55, r=55, t=65, b=45)
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=C['grid'])
    return fig


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.markdown("---")

    # Category filter
    all_cats = sorted(set(ind['categoria'] for ind in INDICADORES))
    selected_cats = st.multiselect(
        "📂 Categorías",
        all_cats,
        default=all_cats,
        help="Filtra indicadores y calendario por categoría"
    )

    # Impact filter
    selected_impact = st.multiselect(
        "⚡ Nivel de impacto",
        ['ALTO', 'MEDIO'],
        default=['ALTO', 'MEDIO']
    )

    # Calendar range
    cal_days = st.slider("📅 Días en calendario", 7, 90, 45, step=7)

    st.markdown("---")

    # Chart history
    chart_start = st.selectbox(
        "📈 Historial de gráficas",
        ['2020-01-01', '2018-01-01', '2015-01-01', '2010-01-01', '2005-01-01'],
        index=2,
        format_func=lambda x: f"Desde {x[:4]}"
    )

    st.markdown("---")
    st.markdown(
        f"<p style='font-size:0.75rem; color:{C['text_secondary']};'>"
        f"📡 Datos: FRED API (St. Louis Fed)<br>"
        f"🔄 Cache: 1 hora<br>"
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC</p>",
        unsafe_allow_html=True
    )


# ============================================================
# MAIN CONTENT
# ============================================================

# ── Header ──
st.markdown(f"""
<div class='main-header'>
    <h1>🏛️ US Economic Calendar
        <span class='live-badge'>● LIVE</span>
    </h1>
    <p>Macro Research Dashboard — Datos económicos de EE.UU., consenso, históricos y monitor FOMC</p>
</div>
""", unsafe_allow_html=True)


# ── KPI Cards: fetch key data ──
with st.spinner("Cargando indicadores clave..."):
    kpi_data = {}
    for fid, name in [('CPIAUCSL', 'CPI'), ('UNRATE', 'Desempleo'), ('FEDFUNDS', 'Fed Rate'), ('T10Y2Y', 'Curva 10Y-2Y')]:
        data = fetch_fred_data(fid, '2022-01-01')
        ind = next((i for i in INDICADORES if i['fred_id'] == fid), None)
        if data is not None and ind:
            transformed, unit = apply_transform(data, ind['transform'])
            if transformed is not None and len(transformed) > 1:
                kpi_data[name] = {
                    'value': transformed.iloc[-1],
                    'prev': transformed.iloc[-2],
                    'unit': unit,
                }

kpi_cols = st.columns(4)
kpi_configs = [
    ('CPI', '🔥 CPI YoY'),
    ('Desempleo', '👷 Desempleo'),
    ('Fed Rate', '🏦 Fed Funds'),
    ('Curva 10Y-2Y', '📉 Curva 10Y-2Y'),
]

for col, (key, label) in zip(kpi_cols, kpi_configs):
    with col:
        if key in kpi_data:
            v = kpi_data[key]['value']
            delta = v - kpi_data[key]['prev']
            delta_class = 'kpi-delta-up' if delta > 0 else ('kpi-delta-down' if delta < 0 else 'kpi-delta-neutral')
            delta_str = f"+{delta:.2f}" if delta > 0 else f"{delta:.2f}"
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-value'>{v:.2f}<span style='font-size:0.9rem;'>{kpi_data[key]['unit']}</span></div>
                <div class='kpi-label'>{label}</div>
                <div class='{delta_class}'>Δ {delta_str} vs anterior</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='kpi-card'>
                <div class='kpi-value'>—</div>
                <div class='kpi-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)


# ── SECTION 1: Economic Calendar ──
st.markdown("""
<div class='section-header'>
    <h2>📅 Próximas Publicaciones</h2>
    <p>Calendario económico de EE.UU. con dato anterior y estimación de consenso</p>
</div>
""", unsafe_allow_html=True)

with st.spinner("Construyendo calendario..."):
    events = build_calendar(days_ahead=cal_days)

# Filter events
filtered_events = [
    e for e in events
    if e['impact'] in selected_impact
    and any(
        ind['categoria'] in selected_cats
        for ind in INDICADORES if ind['fred_id'] == e['fred_id']
    )
]

if filtered_events:
    # Build HTML table
    rows_html = ""
    for e in filtered_events:
        if e['impact'] == 'ALTO':
            badge = "<span class='badge-high'>ALTO</span>"
        else:
            badge = "<span class='badge-med'>MEDIO</span>"

        d = e['days_until']
        if d == 0:
            chip = "<span class='countdown-today'>HOY</span>"
        elif d <= 3:
            chip = f"<span class='countdown-urgent'>{d}d</span>"
        else:
            chip = f"<span class='countdown'>{d}d</span>"

        rows_html += f"""
        <tr>
            <td><strong>{e['date_str']}</strong></td>
            <td style='font-family:JetBrains Mono,monospace; font-size:0.82rem;'>{e['time']} ET</td>
            <td><strong>{e['event']}</strong></td>
            <td>{badge}</td>
            <td style='font-family:JetBrains Mono,monospace;'>{e['previous']}</td>
            <td style='font-family:JetBrains Mono,monospace; color:{C["accent"]}; font-weight:600;'>{e['consensus']}</td>
            <td>{chip}</td>
        </tr>
        """

    st.markdown(f"""
    <table class='cal-table'>
        <thead>
            <tr>
                <th>Fecha</th><th>Hora</th><th>Evento</th>
                <th>Impacto</th><th>Anterior</th><th>Consenso Est.</th><th>Countdown</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    <p style='font-size:0.72rem; color:{C["text_secondary"]}; margin-top:8px;'>
    ⚠️ Consenso = estimación basada en tendencia reciente (media 3 periodos). 
    Para consenso de mercado en tiempo real, consultar Bloomberg / Reuters.
    </p>
    """, unsafe_allow_html=True)
else:
    st.info("No hay eventos que coincidan con los filtros seleccionados.")


# ── SECTION 2: FOMC Monitor ──
st.markdown("""
<div class='section-header'>
    <h2>🏦 Monitor FOMC</h2>
    <p>Próximas reuniones del Federal Open Market Committee</p>
</div>
""", unsafe_allow_html=True)

fomc_col1, fomc_col2 = st.columns([1.3, 2])

with fomc_col1:
    fomc = get_upcoming_fomc()[:8]
    if fomc:
        rows = ""
        for m in fomc:
            hl = "class='fomc-soon'" if m['days'] <= 14 else ""
            d_chip = f"<span class='countdown-urgent'>{m['days']}d</span>" if m['days'] <= 7 else f"<span class='countdown'>{m['days']}d</span>"
            rows += f"""<tr {hl}>
                <td><strong>{m['date']}</strong></td>
                <td>{m['type']}</td>
                <td>{m['dot_plot']}</td>
                <td>{d_chip}</td>
            </tr>"""

        st.markdown(f"""
        <table class='cal-table'>
            <thead><tr><th>Fecha</th><th>Tipo</th><th>Dot Plot</th><th>En</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        """, unsafe_allow_html=True)

with fomc_col2:
    ff_data = fetch_fred_data('FEDFUNDS', start='2000-01-01')
    if ff_data is not None:
        fig_ff = go.Figure()
        fig_ff.add_trace(go.Scatter(
            x=ff_data.index, y=ff_data.values,
            fill='tozeroy', fillcolor='rgba(10,15,26,0.07)',
            line=dict(color=C['line1'], width=2),
            name='Fed Funds Rate',
            hovertemplate='%{x|%b %Y}: <b>%{y:.2f}%</b><extra></extra>'
        ))
        fig_ff.update_layout(
            title=dict(text="<b>Federal Funds Rate</b> — Histórico", x=0.01, font=dict(size=13, family='DM Sans')),
            yaxis_title='%', plot_bgcolor='white', paper_bgcolor='white',
            height=350, margin=dict(l=50, r=20, t=50, b=40),
            hovermode='x unified', showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor=C['grid'])
        )
        st.plotly_chart(fig_ff, use_container_width=True)


# ── SECTION 3: Historical Charts ──
st.markdown("""
<div class='section-header'>
    <h2>📈 Gráficas Históricas</h2>
    <p>Series de tiempo interactivas para cada indicador clave</p>
</div>
""", unsafe_allow_html=True)

# Filter indicators
filtered_indicators = [
    ind for ind in INDICADORES
    if ind['categoria'] in selected_cats and ind['impacto'] in selected_impact
]

# Group by category
cats_shown = []
for ind in filtered_indicators:
    cat_key = f"{ind['cat_icon']} {ind['categoria']}"
    if cat_key not in cats_shown:
        cats_shown.append(cat_key)
        st.markdown(f"#### {cat_key}")

    fig = create_chart(ind, height=400)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption(f"⚠️ {ind['nombre_corto']}: datos no disponibles")

    # Reset category tracking after showing header once
    # (handled by cats_shown list above)


# ── SECTION 4: Comparativos ──
st.markdown("""
<div class='section-header'>
    <h2>🔀 Comparativos Multi-Indicador</h2>
    <p>Cruces entre indicadores para identificar patrones macro</p>
</div>
""", unsafe_allow_html=True)

comp_col1, comp_col2 = st.columns(2)

with comp_col1:
    inds_inflation = [i for i in INDICADORES if i['fred_id'] in ['CPIAUCSL', 'PCEPILFE']]
    fig_comp1 = create_multi_chart(inds_inflation, 'CPI vs Core PCE — ¿Converge al 2%?')
    if fig_comp1:
        fig_comp1.add_hline(y=2.0, line_dash='dot', line_color=C['green'],
                            annotation_text='Target 2%', annotation_font=dict(color=C['green']))
        st.plotly_chart(fig_comp1, use_container_width=True)

with comp_col2:
    inds_emp = [i for i in INDICADORES if i['fred_id'] in ['UNRATE', 'CPIAUCSL']]
    fig_comp2 = create_multi_chart(inds_emp, 'Desempleo vs Inflación (Phillips Curve)')
    if fig_comp2:
        st.plotly_chart(fig_comp2, use_container_width=True)


# ── SECTION 5: Deep Dive ──
st.markdown("""
<div class='section-header'>
    <h2>🔬 Análisis Detallado por Indicador</h2>
    <p>Selecciona un indicador para ver estadísticas y distribución histórica</p>
</div>
""", unsafe_allow_html=True)

selected_name = st.selectbox(
    "Indicador",
    [ind['nombre_corto'] for ind in INDICADORES],
    label_visibility='collapsed'
)

ind = next((i for i in INDICADORES if i['nombre_corto'] == selected_name), None)

if ind:
    data = fetch_fred_data(ind['fred_id'], start=chart_start)
    if data is not None:
        transformed, unit = apply_transform(data, ind['transform'])
        if transformed is not None and len(transformed) > 5:
            # Info box
            st.markdown(f"""
            <div style='background:#f7f9fc; padding:1rem 1.5rem; border-left:4px solid {C["bg_dark"]};
                        border-radius:0 8px 8px 0; margin:1rem 0;'>
                <strong style='font-size:1.05rem;'>{ind['nombre']}</strong><br>
                <span style='color:{C["text_secondary"]}; font-size:0.85rem;'>{ind['descripcion']}</span><br>
                <span style='font-size:0.8rem;'>Fuente: {ind['fuente']} · Frecuencia: {ind['frecuencia']} · FRED: <code>{ind['fred_id']}</code></span>
            </div>
            """, unsafe_allow_html=True)

            # Stats row
            stats_cols = st.columns(5)
            stats = [
                ('Último', f"{transformed.iloc[-1]:.2f}", unit),
                ('Media', f"{transformed.mean():.2f}", ''),
                ('Máximo', f"{transformed.max():.2f}", ''),
                ('Mínimo', f"{transformed.min():.2f}", ''),
                ('Volatilidad', f"{transformed.std():.2f}", 'σ'),
            ]
            for col, (label, val, u) in zip(stats_cols, stats):
                with col:
                    st.metric(label, f"{val} {u}")

            # Chart
            fig_deep = create_chart(ind, height=450)
            if fig_deep:
                st.plotly_chart(fig_deep, use_container_width=True)

            # Distribution
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Histogram(
                x=transformed.values, nbinsx=40,
                marker_color=C['accent'], opacity=0.7,
            ))
            fig_dist.add_vline(x=transformed.iloc[-1], line_color=C['red'], line_dash='dash',
                               annotation_text=f'Actual: {transformed.iloc[-1]:.2f}')
            fig_dist.update_layout(
                title=dict(text=f"<b>Distribución Histórica</b> — {ind['nombre_corto']}", x=0.01,
                           font=dict(size=13, family='DM Sans')),
                xaxis_title=unit, yaxis_title='Frecuencia',
                plot_bgcolor='white', paper_bgcolor='white',
                height=320, margin=dict(l=50, r=20, t=50, b=40)
            )
            st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.warning("No se pudieron obtener datos para este indicador.")


# ── Footer ──
st.markdown("---")
st.markdown(f"""
<div style='text-align:center; padding:1rem; color:{C["text_secondary"]}; font-size:0.78rem;'>
    <strong>US Economic Calendar</strong> — Macro Research Dashboard<br>
    Datos: FRED (Federal Reserve Bank of St. Louis) · Sin costo · Actualización automática al cargar<br>
    ⚠️ El consenso mostrado es una estimación estadística, no el consenso real de mercado.<br>
    Este dashboard no constituye asesoría de inversión.
</div>
""", unsafe_allow_html=True)
