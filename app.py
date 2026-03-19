"""
🏛️ US ECONOMIC CALENDAR — v3 FINAL
=====================================
Premium macro research dashboard.
FRED API key integrated. Production-ready.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import calendar as cal_mod
from fredapi import Fred
import time

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="US Macro Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

FRED_KEY = "a9912f412f890fe14bbaf73000c76838"


# ============================================================
# PREMIUM CSS — Bloomberg meets Figma
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

/* ─── GLOBAL ────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}
.block-container {
    padding: 1.5rem 2rem 2rem 2rem !important;
    max-width: 1400px;
}
h1, h2, h3, h4 { font-family: 'Outfit', sans-serif !important; }

/* ─── HERO BANNER ───────────────────────── */
.hero {
    background: linear-gradient(140deg, #020617 0%, #0f172a 40%, #1e293b 100%);
    border-radius: 16px;
    padding: 2.2rem 2.8rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.06);
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -20%;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: 10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero h1 {
    color: #f1f5f9;
    font-weight: 800;
    font-size: 2rem;
    margin: 0 0 4px 0;
    letter-spacing: -0.8px;
    position: relative;
}
.hero .sub {
    color: #64748b;
    font-size: 0.88rem;
    font-weight: 400;
    position: relative;
}
.hero .live {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16,185,129,0.15);
    color: #34d399;
    font-size: 0.7rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 100px;
    margin-left: 14px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    position: relative;
}
.hero .live::before {
    content: '';
    width: 6px;
    height: 6px;
    background: #34d399;
    border-radius: 50%;
    animation: blink 1.5s infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ─── KPI STRIP ─────────────────────────── */
.kpi-strip {
    display: flex;
    gap: 14px;
    margin-bottom: 1.6rem;
    flex-wrap: wrap;
}
.kpi {
    flex: 1;
    min-width: 200px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 18px 22px;
    position: relative;
    overflow: hidden;
    transition: all 0.2s ease;
}
.kpi:hover {
    border-color: #cbd5e1;
    box-shadow: 0 4px 24px rgba(0,0,0,0.04);
    transform: translateY(-1px);
}
.kpi .tag {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #94a3b8;
    margin-bottom: 6px;
}
.kpi .val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.9rem;
    font-weight: 600;
    color: #0f172a;
    line-height: 1;
}
.kpi .unit {
    font-size: 0.85rem;
    color: #94a3b8;
    font-weight: 400;
}
.kpi .delta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    font-weight: 500;
    margin-top: 6px;
}
.kpi .delta.up { color: #10b981; }
.kpi .delta.dn { color: #ef4444; }
.kpi .delta.flat { color: #94a3b8; }
.kpi .spark {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 100px;
    height: 45px;
    opacity: 0.12;
}

/* ─── SECTION LABEL ─────────────────────── */
.sec {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 2.2rem 0 1rem 0;
    padding-bottom: 10px;
    border-bottom: 2px solid #0f172a;
}
.sec h2 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0f172a;
    margin: 0;
    letter-spacing: -0.3px;
}
.sec .cnt {
    background: #0f172a;
    color: white;
    font-size: 0.65rem;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 100px;
    font-family: 'IBM Plex Mono', monospace;
}

/* ─── CALENDAR TABLE ────────────────────── */
.ctbl {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 14px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
    font-size: 0.84rem;
}
.ctbl thead {
    background: linear-gradient(135deg, #020617, #0f172a);
}
.ctbl th {
    color: #94a3b8;
    padding: 13px 18px;
    text-align: left;
    font-weight: 600;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}
.ctbl td {
    padding: 12px 18px;
    border-bottom: 1px solid #f1f5f9;
    color: #1e293b;
    vertical-align: middle;
}
.ctbl tbody tr {
    transition: background 0.15s;
}
.ctbl tbody tr:hover {
    background: #f8fafc;
}
.ctbl tbody tr:last-child td {
    border-bottom: none;
}
.ctbl .ev {
    font-weight: 600;
    color: #0f172a;
}
.ctbl .mono {
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 500;
}

/* ─── BADGES ────────────────────────────── */
.b-high {
    display: inline-block;
    background: linear-gradient(135deg, #fef2f2, #fee2e2);
    color: #dc2626;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 3px 12px;
    border-radius: 100px;
    letter-spacing: 0.3px;
    border: 1px solid #fecaca;
}
.b-med {
    display: inline-block;
    background: linear-gradient(135deg, #fffbeb, #fef3c7);
    color: #d97706;
    font-size: 0.68rem;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 100px;
    letter-spacing: 0.3px;
    border: 1px solid #fde68a;
}

/* ─── COUNTDOWN CHIPS ───────────────────── */
.cd {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 11px;
    border-radius: 100px;
    display: inline-block;
}
.cd-now {
    background: #dc2626;
    color: white;
    animation: blink 1s infinite;
}
.cd-soon {
    background: #fff7ed;
    color: #ea580c;
    border: 1px solid #fed7aa;
}
.cd-week {
    background: #eff6ff;
    color: #2563eb;
    border: 1px solid #bfdbfe;
}
.cd-later {
    background: #f8fafc;
    color: #94a3b8;
    border: 1px solid #e2e8f0;
}

/* ─── FOMC TABLE ────────────────────────── */
.ftbl {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #e2e8f0;
    font-size: 0.82rem;
}
.ftbl thead { background: #0f172a; }
.ftbl th {
    color: #94a3b8;
    padding: 11px 16px;
    font-weight: 600;
    font-size: 0.66rem;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    text-align: left;
}
.ftbl td {
    padding: 10px 16px;
    border-bottom: 1px solid #f1f5f9;
    color: #334155;
}
.ftbl tbody tr:last-child td { border-bottom: none; }
.ftbl .soon-row { background: #fffbeb !important; }

/* ─── TABS ──────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #f1f5f9;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 10px 24px;
    font-weight: 600;
    font-size: 0.85rem;
    font-family: 'Outfit', sans-serif;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    color: #0f172a !important;
}

/* ─── METRICS ───────────────────────────── */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #f8fafc, #f1f5f9);
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 18px 22px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #0f172a !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.7px !important;
    font-weight: 600 !important;
    color: #94a3b8 !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ─── SIDEBAR ───────────────────────────── */
section[data-testid="stSidebar"] {
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] .stMarkdown h2 {
    font-size: 1rem;
    letter-spacing: -0.2px;
}

/* ─── INFO CARD ─────────────────────────── */
.info-card {
    background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
    border: 1px solid #bae6fd;
    border-radius: 14px;
    padding: 20px 24px;
    margin: 12px 0;
}
.info-card h4 {
    color: #0c4a6e;
    margin: 0 0 4px 0;
    font-weight: 700;
}
.info-card p {
    color: #0369a1;
    font-size: 0.85rem;
    margin: 0;
}
.info-card code {
    background: rgba(3,105,161,0.1);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
}

/* ─── FOOTER ────────────────────────────── */
.foot {
    text-align: center;
    padding: 1.5rem;
    color: #94a3b8;
    font-size: 0.75rem;
    border-top: 1px solid #e2e8f0;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# FRED CONNECTION
# ============================================================
@st.cache_resource
def get_fred():
    return Fred(api_key=FRED_KEY)

fred = get_fred()


# ============================================================
# INDICATOR CATALOG
# ============================================================
IND = [
    # INFLACIÓN
    dict(id='CPIAUCSL', name='CPI — Consumer Price Index', s='CPI', cat='Inflación', ic='🔥',
         fr='Mensual', imp='ALTO', src='BLS', d='Variación de precios al consumidor. El más seguido.', tf='y'),
    dict(id='CPILFESL', name='Core CPI (Ex-Food & Energy)', s='Core CPI', cat='Inflación', ic='🔥',
         fr='Mensual', imp='ALTO', src='BLS', d='CPI subyacente sin alimentos ni energía.', tf='y'),
    dict(id='PCEPI', name='PCE Price Index', s='PCE', cat='Inflación', ic='🔥',
         fr='Mensual', imp='ALTO', src='BEA', d='Indicador de inflación PREFERIDO de la Fed. Meta 2%.', tf='y'),
    dict(id='PCEPILFE', name='Core PCE (Ex-Food & Energy)', s='Core PCE', cat='Inflación', ic='🔥',
         fr='Mensual', imp='ALTO', src='BEA', d='La métrica exacta del objetivo de inflación del 2% de la Fed.', tf='y'),
    dict(id='PPIFIS', name='PPI — Producer Price Index', s='PPI', cat='Inflación', ic='🔥',
         fr='Mensual', imp='MEDIO', src='BLS', d='Precios al productor. Indicador adelantado de inflación.', tf='y'),
    # EMPLEO
    dict(id='PAYEMS', name='Nonfarm Payrolls (NFP)', s='NFP', cat='Empleo', ic='👷',
         fr='Mensual', imp='ALTO', src='BLS', d='Cambio mensual en empleo no agrícola. Mueve mercados.', tf='d'),
    dict(id='UNRATE', name='Unemployment Rate', s='Desempleo', cat='Empleo', ic='👷',
         fr='Mensual', imp='ALTO', src='BLS', d='Tasa de desempleo. Mandato dual de la Fed.', tf='l'),
    dict(id='CES0500000003', name='Average Hourly Earnings', s='Salarios/Hora', cat='Empleo', ic='👷',
         fr='Mensual', imp='ALTO', src='BLS', d='Salario promedio por hora. Presiones inflacionarias laborales.', tf='y'),
    dict(id='ICSA', name='Initial Jobless Claims', s='Jobless Claims', cat='Empleo', ic='👷',
         fr='Semanal', imp='MEDIO', src='DOL', d='Solicitudes semanales de desempleo. Alta frecuencia.', tf='l'),
    dict(id='JTSJOL', name='JOLTS — Job Openings', s='JOLTS', cat='Empleo', ic='👷',
         fr='Mensual', imp='MEDIO', src='BLS', d='Vacantes laborales. Indicador de demanda de trabajo.', tf='l'),
    # ACTIVIDAD
    dict(id='GDP', name='GDP (Gross Domestic Product)', s='PIB', cat='Actividad', ic='📈',
         fr='Trimestral', imp='ALTO', src='BEA', d='Producto Interno Bruto. La medida más amplia de actividad.', tf='a'),
    dict(id='RSAFS', name='Retail Sales (Advance)', s='Retail Sales', cat='Actividad', ic='📈',
         fr='Mensual', imp='ALTO', src='Census', d='Ventas minoristas. Consumo = ~70% del PIB.', tf='m'),
    dict(id='INDPRO', name='Industrial Production', s='Prod. Industrial', cat='Actividad', ic='📈',
         fr='Mensual', imp='MEDIO', src='Fed Board', d='Producción de fábricas, minas y utilidades.', tf='m'),
    # CONFIANZA
    dict(id='UMCSENT', name='U. Michigan Consumer Sentiment', s='UMich', cat='Confianza', ic='🧠',
         fr='Mensual', imp='MEDIO', src='U. Michigan', d='Confianza del consumidor + expectativas de inflación.', tf='l'),
    # MANUFACTURA
    dict(id='DGORDER', name='Durable Goods Orders', s='Durable Goods', cat='Manufactura', ic='🏭',
         fr='Mensual', imp='MEDIO', src='Census', d='Pedidos de bienes duraderos. Proxy de inversión.', tf='m'),
    # VIVIENDA
    dict(id='HOUST', name='Housing Starts', s='Housing Starts', cat='Vivienda', ic='🏠',
         fr='Mensual', imp='MEDIO', src='Census', d='Inicio de construcción de viviendas.', tf='l'),
    dict(id='EXHOSLUSM495S', name='Existing Home Sales', s='Existing Homes', cat='Vivienda', ic='🏠',
         fr='Mensual', imp='MEDIO', src='NAR', d='Ventas de casas existentes.', tf='l'),
    # COMERCIO
    dict(id='BOPGSTB', name='Trade Balance', s='Trade Balance', cat='Comercio', ic='🌍',
         fr='Mensual', imp='MEDIO', src='Census/BEA', d='Exportaciones menos importaciones.', tf='l'),
    # POL. MONETARIA
    dict(id='FEDFUNDS', name='Federal Funds Effective Rate', s='Fed Funds', cat='Pol. Monetaria', ic='🏦',
         fr='Diario', imp='ALTO', src='Federal Reserve', d='Tasa de referencia de la Fed.', tf='l'),
    dict(id='T10Y2Y', name='Treasury Yield Spread (10Y-2Y)', s='Curva 10Y-2Y', cat='Pol. Monetaria', ic='🏦',
         fr='Diario', imp='ALTO', src='Treasury/Fed', d='Spread 10Y-2Y. Inversión = señal de recesión.', tf='l'),
]


# ============================================================
# DATA ENGINE
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load(fid, start='2015-01-01'):
    """Load series from FRED API."""
    try:
        s = fred.get_series(fid, observation_start=start)
        return s.dropna() if s is not None else None
    except Exception:
        return None


def tfm(data, code):
    """Transform series."""
    if data is None or len(data) < 2:
        return None, ''
    try:
        if code == 'y' and len(data) > 12:
            return (data.pct_change(12) * 100).dropna(), '% YoY'
        elif code == 'm':
            return (data.pct_change() * 100).dropna(), '% MoM'
        elif code == 'a':
            return (data.pct_change() * 400).dropna(), '% SAAR'
        elif code == 'd':
            return data.diff().dropna(), 'Chg (K)'
        else:
            return data, ''
    except:
        return data, ''


@st.cache_data(ttl=3600, show_spinner=False)
def get_data(fid, code, start='2015-01-01'):
    raw = load(fid, start)
    t, u = tfm(raw, code)
    return raw, t, u


# ============================================================
# CALENDAR ENGINE
# ============================================================
SCHED = [
    ('Nonfarm Payrolls', 'PAYEMS', 'ff', '08:30', 'ALTO'),
    ('Unemployment Rate', 'UNRATE', 'ff', '08:30', 'ALTO'),
    ('Avg Hourly Earnings', 'CES0500000003', 'ff', '08:30', 'ALTO'),
    ('CPI (All Items)', 'CPIAUCSL', 12, '08:30', 'ALTO'),
    ('Core CPI', 'CPILFESL', 12, '08:30', 'ALTO'),
    ('PPI (Final Demand)', 'PPIFIS', 14, '08:30', 'MEDIO'),
    ('Retail Sales', 'RSAFS', 15, '08:30', 'ALTO'),
    ('PCE Price Index', 'PCEPI', 28, '08:30', 'ALTO'),
    ('Core PCE', 'PCEPILFE', 28, '08:30', 'ALTO'),
    ('Industrial Production', 'INDPRO', 16, '09:15', 'MEDIO'),
    ('Housing Starts', 'HOUST', 18, '08:30', 'MEDIO'),
    ('Durable Goods', 'DGORDER', 26, '08:30', 'MEDIO'),
    ('Consumer Sentiment', 'UMCSENT', 14, '10:00', 'MEDIO'),
    ('JOLTS', 'JTSJOL', 7, '10:00', 'MEDIO'),
    ('Trade Balance', 'BOPGSTB', 6, '08:30', 'MEDIO'),
    ('Initial Claims', 'ICSA', 'thu', '08:30', 'MEDIO'),
]


def nxt(stype, today):
    def mos(n=4):
        y, m = today.year, today.month
        for _ in range(n):
            yield y, m
            m += 1
            if m > 12: m, y = 1, y + 1

    if stype == 'ff':
        for y, m in mos():
            for w in cal_mod.monthcalendar(y, m):
                if w[cal_mod.FRIDAY]:
                    d = datetime(y, m, w[cal_mod.FRIDAY])
                    if d.date() >= today.date(): return d
                    break
    elif stype == 'thu':
        d = today
        while d.weekday() != 3: d += timedelta(days=1)
        return d
    elif isinstance(stype, int):
        for y, m in mos():
            mx = cal_mod.monthrange(y, m)[1]
            d = datetime(y, m, min(stype, mx))
            while d.weekday() >= 5: d += timedelta(days=1)
            if d.date() >= today.date(): return d
    return None


@st.cache_data(ttl=3600, show_spinner="Cargando calendario económico...")
def build_cal(days=60):
    today = datetime.now()
    rows = []
    for name, fid, stype, t_et, imp in SCHED:
        nd = nxt(stype, today)
        if nd is None or (nd - today).days > days: continue

        ind = next((i for i in IND if i['id'] == fid), None)
        prev, cons = '—', '—'
        if ind:
            _, td, u = get_data(fid, ind['tf'], '2020-01-01')
            if td is not None and len(td) > 3:
                lv = td.iloc[-1]
                a3 = td.iloc[-3:].mean()
                if ind['tf'] == 'd':
                    prev, cons = f"{lv:+,.0f}", f"{a3:+,.0f}"
                elif ind['tf'] in ('y', 'm', 'a'):
                    prev, cons = f"{lv:.2f}%", f"{a3:.2f}%"
                else:
                    prev, cons = f"{lv:,.1f}", f"{a3:,.1f}"

        du = (nd - today).days
        rows.append(dict(
            date=nd, fecha=nd.strftime('%b %d'), dia=nd.strftime('%a'),
            hora=t_et, evento=name, fid=fid, imp=imp,
            anterior=prev, consenso=cons, dias=du
        ))
    return sorted(rows, key=lambda x: x['date'])


# ============================================================
# CHART ENGINE
# ============================================================
PLT = dict(
    bg='#ffffff', grid='#f1f5f9',
    c1='#0f172a', c2='#2563eb', c3='#dc2626', c4='#10b981', c5='#d97706',
    fill='rgba(15,23,42,0.04)', fillb='rgba(37,99,235,0.05)',
)


def chart(ind, start='2015-01-01', h=400):
    _, td, u = get_data(ind['id'], ind['tf'], start)
    if td is None or len(td) < 5: return None

    fig = go.Figure()

    # Main line with area
    fig.add_trace(go.Scatter(
        x=td.index, y=td.values, fill='tozeroy',
        fillcolor=PLT['fillb'], line=dict(color=PLT['c1'], width=2.2),
        name=ind['s'],
        hovertemplate='<b>%{x|%b %d, %Y}</b><br>%{y:.2f} ' + u + '<extra></extra>'
    ))

    # MA-6
    if len(td) > 6:
        ma = td.rolling(6).mean()
        fig.add_trace(go.Scatter(
            x=ma.index, y=ma.values,
            line=dict(color=PLT['c5'], width=1.5, dash='dot'),
            name='MA-6', opacity=0.6,
            hovertemplate='MA-6: %{y:.2f}<extra></extra>'
        ))

    # Last value
    lv, ld = td.iloc[-1], td.index[-1]
    fig.add_trace(go.Scatter(
        x=[ld], y=[lv], mode='markers+text',
        marker=dict(color=PLT['c3'], size=8, line=dict(color='white', width=2)),
        text=[f'  {lv:.2f}'], textposition='middle right',
        textfont=dict(size=11, color=PLT['c3'], family='IBM Plex Mono'),
        showlegend=False, hoverinfo='skip'
    ))

    # Fed 2% target
    if ind['cat'] == 'Inflación' and ind['tf'] == 'y':
        fig.add_hline(y=2, line_dash='dot', line_color=PLT['c4'], line_width=1.5,
                      annotation_text='⎯ Fed Target 2%', annotation_position='bottom right',
                      annotation_font=dict(color=PLT['c4'], size=10, family='IBM Plex Mono'))

    # Zero line
    if u.startswith('%'):
        fig.add_hline(y=0, line_color='#e2e8f0', line_width=1)

    # COVID
    if pd.Timestamp('2020-02-01') >= td.index.min():
        fig.add_vrect(x0='2020-02-01', x1='2020-04-01',
                      fillcolor='rgba(220,38,38,0.04)', layer='below', line_width=0)

    fig.update_layout(
        title=dict(
            text=f"<b>{ind['name']}</b><br>"
                 f"<span style='font-size:11px;color:#94a3b8;font-weight:400;'>"
                 f"{ind['src']} · {ind['fr']} · "
                 f"Último: <b style='color:#0f172a'>{lv:.2f}</b> {u} ({ld.strftime('%b %Y')})</span>",
            x=0, font=dict(size=14, family='Outfit')
        ),
        xaxis=dict(
            showgrid=False,
            rangeselector=dict(
                buttons=[
                    dict(count=1, label='1Y', step='year', stepmode='backward'),
                    dict(count=3, label='3Y', step='year', stepmode='backward'),
                    dict(count=5, label='5Y', step='year', stepmode='backward'),
                    dict(step='all', label='Max')
                ],
                bgcolor='#f1f5f9', activecolor='#0f172a',
                font=dict(color='#475569', size=10, family='Outfit'), y=1.05
            )
        ),
        yaxis=dict(showgrid=True, gridcolor=PLT['grid'], gridwidth=1,
                   title=dict(text=u, font=dict(size=10, color='#94a3b8', family='IBM Plex Mono')),
                   zeroline=False),
        plot_bgcolor=PLT['bg'], paper_bgcolor=PLT['bg'],
        height=h, margin=dict(l=55, r=20, t=78, b=40),
        legend=dict(orientation='h', yanchor='bottom', y=1.01, xanchor='right', x=1,
                    font=dict(size=10, color='#64748b', family='Outfit')),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='white', font_size=12, font_family='Outfit',
                        bordercolor='#e2e8f0')
    )
    return fig


def multi_chart(inds, title, h=380):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    pal = [PLT['c1'], PLT['c3'], PLT['c4'], PLT['c5']]
    for i, ind in enumerate(inds):
        _, td, u = get_data(ind['id'], ind['tf'])
        if td is not None:
            fig.add_trace(go.Scatter(
                x=td.index, y=td.values,
                line=dict(color=pal[i % len(pal)], width=2.2),
                name=f"{ind['s']} ({u})",
                hovertemplate=f"{ind['s']}: " + '%{y:.2f}<extra></extra>'
            ), secondary_y=(i == 1))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", x=0, font=dict(size=14, family='Outfit')),
        plot_bgcolor='white', paper_bgcolor='white', height=h,
        hovermode='x unified',
        legend=dict(orientation='h', y=1.08, font=dict(size=10, family='Outfit')),
        margin=dict(l=55, r=55, t=58, b=40),
        hoverlabel=dict(bgcolor='white', font_size=12, font_family='Outfit')
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=PLT['grid'])
    return fig


# ============================================================
# FOMC
# ============================================================
FOMC = [
    ('2025-01-29',0),('2025-03-19',1),('2025-05-07',0),('2025-06-18',1),
    ('2025-07-30',0),('2025-09-17',1),('2025-10-29',0),('2025-12-10',1),
    ('2026-01-28',0),('2026-03-18',1),('2026-05-06',0),('2026-06-17',1),
    ('2026-07-29',0),('2026-09-16',1),('2026-10-28',0),('2026-12-09',1),
]


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    st.divider()
    cats = sorted(set(i['cat'] for i in IND))
    sel_cats = st.multiselect("Categorías", cats, default=cats)
    sel_imp = st.multiselect("Impacto", ['ALTO', 'MEDIO'], default=['ALTO', 'MEDIO'])
    cal_days = st.slider("Días en calendario", 7, 90, 45, 7)
    ch_start = st.selectbox("Historial desde", ['2022-01-01','2020-01-01','2018-01-01','2015-01-01','2010-01-01'],
                            index=3, format_func=lambda x: x[:4])
    st.divider()
    st.caption(f"📡 FRED API · Key: ...{FRED_KEY[-6:]}")
    st.caption(f"🔄 Cache: 1 hora")
    st.caption(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC")


# ============================================================
# HERO
# ============================================================
st.markdown(f"""
<div class="hero">
    <h1>📊 US Economic Calendar<span class="live">LIVE DATA</span></h1>
    <p class="sub">Macro Research Dashboard — Calendario económico, consenso, series históricas & FOMC · {datetime.now().strftime('%B %d, %Y')}</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# KPI STRIP
# ============================================================
kpis = [
    ('CPIAUCSL','y','🔥','CPI YoY'),
    ('UNRATE','l','👷','DESEMPLEO'),
    ('FEDFUNDS','l','🏦','FED FUNDS'),
    ('T10Y2Y','l','📉','CURVA 10Y-2Y'),
]

kpi_html = '<div class="kpi-strip">'
for fid, tf, icon, label in kpis:
    _, td, u = get_data(fid, tf, '2022-01-01')
    if td is not None and len(td) > 1:
        v = td.iloc[-1]
        d = v - td.iloc[-2]
        dcls = 'up' if d > 0 else ('dn' if d < 0 else 'flat')
        dsign = '+' if d > 0 else ''
        kpi_html += f"""
        <div class="kpi">
            <div class="tag">{icon} {label}</div>
            <div class="val">{v:.2f}<span class="unit"> {u}</span></div>
            <div class="delta {dcls}">Δ {dsign}{d:.2f} vs anterior</div>
        </div>"""
    else:
        kpi_html += f"""
        <div class="kpi">
            <div class="tag">{icon} {label}</div>
            <div class="val">—</div>
            <div class="delta flat">cargando...</div>
        </div>"""
kpi_html += '</div>'
st.markdown(kpi_html, unsafe_allow_html=True)


# ============================================================
# TABS
# ============================================================
t1, t2, t3, t4, t5 = st.tabs([
    "📅 Calendario", "📈 Gráficas", "🏦 FOMC", "🔀 Comparativos", "🔬 Deep Dive"
])


# ── TAB 1: CALENDAR ──────────────────────────────────────────
with t1:
    st.markdown("""<div class="sec"><h2>📅 Próximas Publicaciones</h2></div>""", unsafe_allow_html=True)
    st.caption("Calendario económico de EE.UU. · Dato anterior y consenso estimado (media 3 periodos)")

    events = build_cal(cal_days)

    # filter
    cat_fids = {i['id'] for i in IND if i['cat'] in sel_cats}
    evts = [e for e in events if e['imp'] in sel_imp and e['fid'] in cat_fids]

    if evts:
        # Build HTML table
        rows_h = ''
        for e in evts:
            badge = f'<span class="b-high">ALTO</span>' if e['imp'] == 'ALTO' else f'<span class="b-med">MEDIO</span>'
            d = e['dias']
            if d == 0: chip = '<span class="cd cd-now">HOY</span>'
            elif d <= 3: chip = f'<span class="cd cd-soon">{d}d</span>'
            elif d <= 7: chip = f'<span class="cd cd-week">{d}d</span>'
            else: chip = f'<span class="cd cd-later">{d}d</span>'

            rows_h += f"""<tr>
                <td><strong>{e['fecha']}</strong><br><span style="color:#94a3b8;font-size:0.75rem;">{e['dia']}</span></td>
                <td class="mono">{e['hora']} ET</td>
                <td class="ev">{e['evento']}</td>
                <td>{badge}</td>
                <td class="mono">{e['anterior']}</td>
                <td class="mono" style="color:#2563eb;font-weight:600;">{e['consenso']}</td>
                <td>{chip}</td>
            </tr>"""

        st.markdown(f"""
        <table class="ctbl">
            <thead><tr>
                <th>FECHA</th><th>HORA</th><th>EVENTO</th>
                <th>IMPACTO</th><th>ANTERIOR</th><th>CONSENSO</th><th>EN</th>
            </tr></thead>
            <tbody>{rows_h}</tbody>
        </table>
        """, unsafe_allow_html=True)

        # Summary
        st.markdown("")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Total eventos", len(evts))
        mc2.metric("Alto impacto", sum(1 for e in evts if e['imp'] == 'ALTO'))
        if evts:
            mc3.metric("Próximo", evts[0]['evento'], f"en {evts[0]['dias']} días")
    else:
        st.info("No hay eventos con los filtros seleccionados.")

    st.caption("⚠️ Consenso = estimación basada en tendencia reciente. Para consenso real: Bloomberg / Reuters.")


# ── TAB 2: CHARTS ────────────────────────────────────────────
with t2:
    st.markdown("""<div class="sec"><h2>📈 Series Históricas</h2></div>""", unsafe_allow_html=True)
    st.caption("Gráficas interactivas · Botones 1Y/3Y/5Y/Max para cambiar rango · Hover para ver valores")

    flt = [i for i in IND if i['cat'] in sel_cats and i['imp'] in sel_imp]
    if not flt:
        st.info("Selecciona categorías e impacto en el sidebar.")
    else:
        cur = ''
        for ind in flt:
            cl = f"{ind['ic']} {ind['cat']}"
            if cl != cur:
                cur = cl
                st.markdown(f"#### {cl}")
            fig = chart(ind, start=ch_start)
            if fig:
                st.plotly_chart(fig, use_container_width=True, key=f"c_{ind['id']}")
            else:
                st.warning(f"{ind['s']}: datos no disponibles")


# ── TAB 3: FOMC ─────────────────────────────────────────────
with t3:
    st.markdown("""<div class="sec"><h2>🏦 Calendario FOMC</h2></div>""", unsafe_allow_html=True)
    st.caption("Federal Open Market Committee · Decisión 14:00 ET · Conferencia 14:30 ET")

    fc1, fc2 = st.columns([1.2, 2])

    with fc1:
        today = datetime.now().date()
        fomc_rows = ''
        cnt = 0
        for ds, sep in FOMC:
            d = datetime.strptime(ds, '%Y-%m-%d').date()
            if d >= today and cnt < 10:
                dd = (d - today).days
                scls = ' class="soon-row"' if dd <= 14 else ''
                sep_txt = '📊 Regular + SEP' if sep else 'Regular'
                dot = '✅' if sep else '—'
                chip = f'<span class="cd cd-soon">{dd}d</span>' if dd <= 7 else f'<span class="cd cd-week">{dd}d</span>' if dd <= 30 else f'<span class="cd cd-later">{dd}d</span>'
                fomc_rows += f'<tr{scls}><td><strong>{d.strftime("%b %d, %Y")}</strong></td><td>{sep_txt}</td><td>{dot}</td><td>{chip}</td></tr>'
                cnt += 1

        st.markdown(f"""
        <table class="ftbl">
            <thead><tr><th>FECHA</th><th>TIPO</th><th>DOT PLOT</th><th>EN</th></tr></thead>
            <tbody>{fomc_rows}</tbody>
        </table>
        """, unsafe_allow_html=True)

    with fc2:
        raw_ff = load('FEDFUNDS', '2000-01-01')
        if raw_ff is not None:
            fig_ff = go.Figure()
            fig_ff.add_trace(go.Scatter(
                x=raw_ff.index, y=raw_ff.values,
                fill='tozeroy', fillcolor='rgba(15,23,42,0.05)',
                line=dict(color=PLT['c1'], width=2),
                hovertemplate='%{x|%b %Y}: <b>%{y:.2f}%</b><extra></extra>'
            ))
            fig_ff.update_layout(
                title=dict(text="<b>Federal Funds Rate — Histórico</b>", x=0,
                           font=dict(size=14, family='Outfit')),
                yaxis_title='%', plot_bgcolor='white', paper_bgcolor='white',
                height=350, margin=dict(l=50, r=20, t=50, b=40),
                hovermode='x unified', showlegend=False,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor=PLT['grid']),
                hoverlabel=dict(bgcolor='white', font_family='Outfit')
            )
            st.plotly_chart(fig_ff, use_container_width=True)

    # Yield curve
    st.markdown("#### 📉 Curva de Yields — Spread 10Y vs 2Y")
    raw_curve = load('T10Y2Y', '2000-01-01')
    if raw_curve is not None:
        fig_yc = go.Figure()
        colors_fill = ['rgba(220,38,38,0.08)' if v < 0 else 'rgba(16,163,74,0.05)' for v in raw_curve.values]
        fig_yc.add_trace(go.Scatter(
            x=raw_curve.index, y=raw_curve.values,
            fill='tozeroy', fillcolor='rgba(37,99,235,0.05)',
            line=dict(color=PLT['c1'], width=1.5),
            hovertemplate='%{x|%b %Y}: <b>%{y:.2f}%</b><extra></extra>'
        ))
        fig_yc.add_hline(y=0, line_color=PLT['c3'], line_width=1.5, line_dash='dash',
                         annotation_text='Inversión → señal recesión',
                         annotation_font=dict(color=PLT['c3'], size=10, family='IBM Plex Mono'))
        fig_yc.update_layout(
            title=dict(text="<b>Treasury Yield Spread 10Y - 2Y</b>", x=0,
                       font=dict(size=14, family='Outfit')),
            yaxis_title='%', plot_bgcolor='white', paper_bgcolor='white',
            height=340, margin=dict(l=50, r=20, t=50, b=40),
            hovermode='x unified', showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor=PLT['grid']),
        )
        st.plotly_chart(fig_yc, use_container_width=True)


# ── TAB 4: COMPARISONS ──────────────────────────────────────
with t4:
    st.markdown("""<div class="sec"><h2>🔀 Comparativos</h2></div>""", unsafe_allow_html=True)

    cc1, cc2 = st.columns(2)
    with cc1:
        ids = [i for i in IND if i['id'] in ('CPIAUCSL', 'PCEPILFE')]
        f1 = multi_chart(ids, 'CPI vs Core PCE — ¿Converge al 2%?')
        f1.add_hline(y=2, line_dash='dot', line_color=PLT['c4'],
                     annotation_text='Target 2%', annotation_font=dict(color=PLT['c4'], size=10))
        st.plotly_chart(f1, use_container_width=True)

    with cc2:
        ids2 = [i for i in IND if i['id'] in ('UNRATE', 'CPIAUCSL')]
        f2 = multi_chart(ids2, 'Desempleo vs Inflación (Phillips Curve)')
        st.plotly_chart(f2, use_container_width=True)

    st.divider()
    st.markdown("#### 🎛️ Comparativo personalizado")
    pc1, pc2 = st.columns(2)
    names = [i['s'] for i in IND]
    with pc1: s1 = st.selectbox("Indicador 1", names, 0)
    with pc2: s2 = st.selectbox("Indicador 2", names, 6)
    if s1 != s2:
        ci = [i for i in IND if i['s'] in (s1, s2)]
        fc = multi_chart(ci, f'{s1} vs {s2}')
        st.plotly_chart(fc, use_container_width=True)


# ── TAB 5: DEEP DIVE ────────────────────────────────────────
with t5:
    st.markdown("""<div class="sec"><h2>🔬 Análisis Detallado</h2></div>""", unsafe_allow_html=True)

    sn = st.selectbox("Selecciona indicador", [i['s'] for i in IND], label_visibility='collapsed')
    ind = next((i for i in IND if i['s'] == sn), None)

    if ind:
        st.markdown(f"""
        <div class="info-card">
            <h4>{ind['ic']} {ind['name']}</h4>
            <p>{ind['d']}<br>
            Fuente: <strong>{ind['src']}</strong> · Frecuencia: <strong>{ind['fr']}</strong> · FRED: <code>{ind['id']}</code></p>
        </div>
        """, unsafe_allow_html=True)

        _, td, u = get_data(ind['id'], ind['tf'], ch_start)
        if td is not None and len(td) > 5:
            sc = st.columns(5)
            sc[0].metric("Último", f"{td.iloc[-1]:.2f} {u}")
            sc[1].metric("Media", f"{td.mean():.2f}")
            sc[2].metric("Máximo", f"{td.max():.2f}")
            sc[3].metric("Mínimo", f"{td.min():.2f}")
            sc[4].metric("Volatilidad σ", f"{td.std():.2f}")

            fig_d = chart(ind, ch_start, 440)
            if fig_d:
                st.plotly_chart(fig_d, use_container_width=True, key='dd_chart')

            # Distribution
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Histogram(
                x=td.values, nbinsx=40,
                marker_color=PLT['c2'], opacity=0.65,
            ))
            fig_dist.add_vline(x=td.iloc[-1], line_color=PLT['c3'], line_dash='dash',
                               annotation_text=f'Actual: {td.iloc[-1]:.2f}',
                               annotation_font=dict(color=PLT['c3'], family='IBM Plex Mono'))
            fig_dist.add_vline(x=td.mean(), line_color=PLT['c4'], line_dash='dot',
                               annotation_text=f'Media: {td.mean():.2f}',
                               annotation_position='top left',
                               annotation_font=dict(color=PLT['c4'], family='IBM Plex Mono'))
            fig_dist.update_layout(
                title=dict(text=f"<b>Distribución Histórica — {ind['s']}</b>", x=0,
                           font=dict(size=14, family='Outfit')),
                xaxis_title=u, yaxis_title='Frecuencia',
                plot_bgcolor='white', paper_bgcolor='white',
                height=300, margin=dict(l=50, r=20, t=50, b=40),
                showlegend=False
            )
            st.plotly_chart(fig_dist, use_container_width=True, key='dd_dist')

            # Percentile
            pct = (td < td.iloc[-1]).mean() * 100
            st.progress(min(int(pct), 100),
                        text=f"📊 Percentil actual: **{pct:.0f}%** — el valor actual es mayor que el {pct:.0f}% de las observaciones desde {ch_start[:4]}")
        else:
            st.warning("No se pudieron obtener datos.")


# ── FOOTER ───────────────────────────────────────────────────
st.markdown("""
<div class="foot">
    <strong>US Economic Calendar</strong> · Macro Research Dashboard<br>
    Fuente: FRED API (Federal Reserve Bank of St. Louis) · Actualización automática al cargar (cache 1hr)<br>
    ⚠️ El consenso es una estimación estadística, no el consenso real de mercado. No constituye asesoría de inversión.
</div>
""", unsafe_allow_html=True)
