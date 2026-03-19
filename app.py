"""
🏛️ US Economic Calendar — Macro Research Dashboard
====================================================
v2.0 — Native Streamlit components (no raw HTML issues)
Inspired by Trading Economics visual style
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import calendar as cal_module
import requests
import io

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
# MINIMAL SAFE CSS (only styling, no structural HTML)
# ============================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    /* Global font */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    
    /* Remove default padding */
    .block-container { padding-top: 1rem; }
    
    /* Metric cards styling */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        font-weight: 600 !important;
        color: #64748b !important;
    }
    [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        background: #f1f5f9;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Dataframe styling */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #f8fafc;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdown"] p {
        font-size: 0.85rem;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Divider */
    hr {
        border-color: #e2e8f0 !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# COLOR PALETTE
# ============================================================
COLORS = {
    'primary': '#0f172a',
    'accent': '#2563eb',
    'green': '#16a34a',
    'red': '#dc2626',
    'orange': '#ea580c',
    'gold': '#d97706',
    'gray': '#64748b',
    'light': '#f1f5f9',
    'grid': '#f1f5f9',
    'bg': '#ffffff',
    # Chart lines
    'c1': '#0f172a',
    'c2': '#2563eb',
    'c3': '#dc2626',
    'c4': '#16a34a',
    'c5': '#d97706',
}


# ============================================================
# INDICADORES CATALOG
# ============================================================
INDICADORES = [
    # INFLACIÓN
    {'fred_id': 'CPIAUCSL', 'nombre': 'CPI — Consumer Price Index', 'short': 'CPI',
     'cat': 'Inflación', 'icon': '🔥', 'freq': 'Mensual', 'impact': 'ALTO',
     'source': 'BLS', 'desc': 'Variación de precios al consumidor. El indicador de inflación más seguido.', 'tf': 'pct12'},
    {'fred_id': 'CPILFESL', 'nombre': 'Core CPI (Ex-Food & Energy)', 'short': 'Core CPI',
     'cat': 'Inflación', 'icon': '🔥', 'freq': 'Mensual', 'impact': 'ALTO',
     'source': 'BLS', 'desc': 'CPI excluyendo alimentos y energía — inflación subyacente.', 'tf': 'pct12'},
    {'fred_id': 'PCEPI', 'nombre': 'PCE Price Index', 'short': 'PCE',
     'cat': 'Inflación', 'icon': '🔥', 'freq': 'Mensual', 'impact': 'ALTO',
     'source': 'BEA', 'desc': 'Indicador de inflación PREFERIDO de la Fed. Meta: 2%.', 'tf': 'pct12'},
    {'fred_id': 'PCEPILFE', 'nombre': 'Core PCE (Ex-Food & Energy)', 'short': 'Core PCE',
     'cat': 'Inflación', 'icon': '🔥', 'freq': 'Mensual', 'impact': 'ALTO',
     'source': 'BEA', 'desc': 'La métrica que la Fed usa para su objetivo de inflación del 2%.', 'tf': 'pct12'},
    {'fred_id': 'PPIFIS', 'nombre': 'PPI — Producer Price Index', 'short': 'PPI',
     'cat': 'Inflación', 'icon': '🔥', 'freq': 'Mensual', 'impact': 'MEDIO',
     'source': 'BLS', 'desc': 'Precios a nivel productor. Indicador adelantado de inflación.', 'tf': 'pct12'},

    # EMPLEO
    {'fred_id': 'PAYEMS', 'nombre': 'Nonfarm Payrolls (NFP)', 'short': 'NFP',
     'cat': 'Empleo', 'icon': '👷', 'freq': 'Mensual', 'impact': 'ALTO',
     'source': 'BLS', 'desc': 'Cambio mensual en empleo no agrícola. El dato que más mueve mercados.', 'tf': 'diff'},
    {'fred_id': 'UNRATE', 'nombre': 'Unemployment Rate', 'short': 'Desempleo',
     'cat': 'Empleo', 'icon': '👷', 'freq': 'Mensual', 'impact': 'ALTO',
     'source': 'BLS', 'desc': 'Tasa de desempleo. Parte del mandato dual de la Fed.', 'tf': 'level'},
    {'fred_id': 'CES0500000003', 'nombre': 'Average Hourly Earnings', 'short': 'Salarios/Hora',
     'cat': 'Empleo', 'icon': '👷', 'freq': 'Mensual', 'impact': 'ALTO',
     'source': 'BLS', 'desc': 'Salario promedio por hora. Presiones inflacionarias laborales.', 'tf': 'pct12'},
    {'fred_id': 'ICSA', 'nombre': 'Initial Jobless Claims', 'short': 'Jobless Claims',
     'cat': 'Empleo', 'icon': '👷', 'freq': 'Semanal', 'impact': 'MEDIO',
     'source': 'DOL', 'desc': 'Solicitudes semanales de seguro de desempleo.', 'tf': 'level'},
    {'fred_id': 'JTSJOL', 'nombre': 'JOLTS — Job Openings', 'short': 'JOLTS',
     'cat': 'Empleo', 'icon': '👷', 'freq': 'Mensual', 'impact': 'MEDIO',
     'source': 'BLS', 'desc': 'Vacantes laborales. La Fed lo monitorea de cerca.', 'tf': 'level'},

    # ACTIVIDAD / PIB
    {'fred_id': 'GDP', 'nombre': 'GDP — Gross Domestic Product', 'short': 'PIB',
     'cat': 'Actividad', 'icon': '📈', 'freq': 'Trimestral', 'impact': 'ALTO',
     'source': 'BEA', 'desc': 'Producto Interno Bruto.', 'tf': 'pct_ann'},
    {'fred_id': 'RSAFS', 'nombre': 'Retail Sales (Advance)', 'short': 'Retail Sales',
     'cat': 'Actividad', 'icon': '📈', 'freq': 'Mensual', 'impact': 'ALTO',
     'source': 'Census', 'desc': 'Ventas al por menor. Consumo = ~70% del PIB.', 'tf': 'pct'},
    {'fred_id': 'INDPRO', 'nombre': 'Industrial Production', 'short': 'Prod. Industrial',
     'cat': 'Actividad', 'icon': '📈', 'freq': 'Mensual', 'impact': 'MEDIO',
     'source': 'Fed Board', 'desc': 'Producción industrial de fábricas, minas y utilidades.', 'tf': 'pct'},

    # CONFIANZA
    {'fred_id': 'UMCSENT', 'nombre': 'U. Michigan Consumer Sentiment', 'short': 'UMich Sentiment',
     'cat': 'Confianza', 'icon': '🧠', 'freq': 'Mensual', 'impact': 'MEDIO',
     'source': 'U. Michigan', 'desc': 'Confianza del consumidor + expectativas de inflación.', 'tf': 'level'},

    # MANUFACTURA
    {'fred_id': 'DGORDER', 'nombre': 'Durable Goods Orders', 'short': 'Durable Goods',
     'cat': 'Manufactura', 'icon': '🏭', 'freq': 'Mensual', 'impact': 'MEDIO',
     'source': 'Census', 'desc': 'Pedidos de bienes duraderos. Proxy de inversión empresarial.', 'tf': 'pct'},

    # VIVIENDA
    {'fred_id': 'HOUST', 'nombre': 'Housing Starts', 'short': 'Housing Starts',
     'cat': 'Vivienda', 'icon': '🏠', 'freq': 'Mensual', 'impact': 'MEDIO',
     'source': 'Census', 'desc': 'Inicio de construcción de viviendas.', 'tf': 'level'},
    {'fred_id': 'EXHOSLUSM495S', 'nombre': 'Existing Home Sales', 'short': 'Existing Homes',
     'cat': 'Vivienda', 'icon': '🏠', 'freq': 'Mensual', 'impact': 'MEDIO',
     'source': 'NAR', 'desc': 'Ventas de casas existentes.', 'tf': 'level'},

    # COMERCIO
    {'fred_id': 'BOPGSTB', 'nombre': 'Trade Balance', 'short': 'Trade Balance',
     'cat': 'Comercio', 'icon': '🌍', 'freq': 'Mensual', 'impact': 'MEDIO',
     'source': 'Census/BEA', 'desc': 'Exportaciones menos importaciones.', 'tf': 'level'},

    # POLÍTICA MONETARIA
    {'fred_id': 'FEDFUNDS', 'nombre': 'Federal Funds Rate', 'short': 'Fed Funds',
     'cat': 'Pol. Monetaria', 'icon': '🏦', 'freq': 'Diario', 'impact': 'ALTO',
     'source': 'Federal Reserve', 'desc': 'Tasa de referencia de la Fed.', 'tf': 'level'},
    {'fred_id': 'T10Y2Y', 'nombre': 'Yield Spread 10Y-2Y', 'short': 'Curva 10Y-2Y',
     'cat': 'Pol. Monetaria', 'icon': '🏦', 'freq': 'Diario', 'impact': 'ALTO',
     'source': 'Treasury/Fed', 'desc': 'Spread 10Y-2Y. Inversión = señal de recesión.', 'tf': 'level'},
]


# ============================================================
# DATA FUNCTIONS
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fred(fred_id, start='2015-01-01'):
    """Fetch from FRED public CSV — no API key needed."""
    try:
        url = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={fred_id}&cosd={start}'
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text), parse_dates=['DATE'], index_col='DATE')
        col = df.columns[0]
        df[col] = pd.to_numeric(df[col], errors='coerce')
        series = df[col].dropna()
        return series if len(series) > 0 else None
    except Exception:
        return None


def transform(data, tf_type):
    """Apply transformation to series."""
    if data is None or len(data) < 2:
        return None, ''
    try:
        if tf_type == 'pct12' and len(data) > 12:
            return (data.pct_change(12) * 100).dropna(), '% YoY'
        elif tf_type == 'pct':
            return (data.pct_change() * 100).dropna(), '% MoM'
        elif tf_type == 'pct_ann':
            return (data.pct_change() * 400).dropna(), '% SAAR'
        elif tf_type == 'diff':
            return data.diff().dropna(), 'Cambio (K)'
        else:
            return data, 'Nivel'
    except Exception:
        return data, 'Nivel'


@st.cache_data(ttl=3600, show_spinner=False)
def get_indicator_data(fred_id, tf_type, start='2015-01-01'):
    """Fetch + transform in one cached call."""
    raw = fetch_fred(fred_id, start)
    if raw is None:
        return None, None, ''
    tf_data, unit = transform(raw, tf_type)
    return raw, tf_data, unit


# ============================================================
# CALENDAR FUNCTIONS
# ============================================================
SCHEDULE = [
    ('Nonfarm Payrolls', 'PAYEMS', 'ff', '08:30', 'ALTO'),
    ('Unemployment Rate', 'UNRATE', 'ff', '08:30', 'ALTO'),
    ('Avg Hourly Earnings', 'CES0500000003', 'ff', '08:30', 'ALTO'),
    ('CPI (All Items)', 'CPIAUCSL', 'd12', '08:30', 'ALTO'),
    ('Core CPI', 'CPILFESL', 'd12', '08:30', 'ALTO'),
    ('PPI (Final Demand)', 'PPIFIS', 'd14', '08:30', 'MEDIO'),
    ('Retail Sales', 'RSAFS', 'd15', '08:30', 'ALTO'),
    ('PCE Price Index', 'PCEPI', 'd28', '08:30', 'ALTO'),
    ('Core PCE', 'PCEPILFE', 'd28', '08:30', 'ALTO'),
    ('Industrial Production', 'INDPRO', 'd16', '09:15', 'MEDIO'),
    ('Housing Starts', 'HOUST', 'd18', '08:30', 'MEDIO'),
    ('Durable Goods', 'DGORDER', 'd26', '08:30', 'MEDIO'),
    ('Consumer Sentiment', 'UMCSENT', 'd14', '10:00', 'MEDIO'),
    ('JOLTS Job Openings', 'JTSJOL', 'd7', '10:00', 'MEDIO'),
    ('Trade Balance', 'BOPGSTB', 'd6', '08:30', 'MEDIO'),
    ('Initial Claims', 'ICSA', 'thu', '08:30', 'MEDIO'),
]


def next_release(stype, today):
    """Calculate next release date."""
    def months_gen(n=4):
        y, m = today.year, today.month
        for _ in range(n):
            yield y, m
            m += 1
            if m > 12:
                m, y = 1, y + 1

    if stype == 'ff':  # First Friday
        for y, m in months_gen():
            c = cal_module.monthcalendar(y, m)
            for w in c:
                if w[cal_module.FRIDAY] != 0:
                    d = datetime(y, m, w[cal_module.FRIDAY])
                    if d.date() >= today.date():
                        return d
                    break

    elif stype == 'thu':  # Next Thursday
        d = today
        while d.weekday() != 3:
            d += timedelta(days=1)
        return d

    elif stype.startswith('d'):  # Day of month
        target = int(stype[1:])
        for y, m in months_gen():
            mx = cal_module.monthrange(y, m)[1]
            d = datetime(y, m, min(target, mx))
            while d.weekday() >= 5:
                d += timedelta(days=1)
            if d.date() >= today.date():
                return d

    return None


@st.cache_data(ttl=3600, show_spinner="📅 Cargando calendario...")
def build_calendar(days_ahead=60):
    """Build economic calendar with previous values and consensus estimates."""
    today = datetime.now()
    rows = []

    for name, fid, stype, time_et, impact in SCHEDULE:
        nd = next_release(stype, today)
        if nd is None or (nd - today).days > days_ahead:
            continue

        # Fetch data for previous & consensus
        ind = next((i for i in INDICADORES if i['fred_id'] == fid), None)
        prev_val = '—'
        cons_val = '—'

        if ind:
            _, tf_data, unit = get_indicator_data(fid, ind['tf'], '2020-01-01')
            if tf_data is not None and len(tf_data) > 3:
                last = tf_data.iloc[-1]
                avg3 = tf_data.iloc[-3:].mean()

                if ind['tf'] == 'diff':
                    prev_val = f"{last:+,.0f}"
                    cons_val = f"{avg3:+,.0f}"
                elif ind['tf'] in ('pct12', 'pct', 'pct_ann'):
                    prev_val = f"{last:.2f}%"
                    cons_val = f"{avg3:.2f}%"
                else:
                    prev_val = f"{last:,.1f}"
                    cons_val = f"{avg3:,.1f}"

        days_until = (nd - today).days
        rows.append({
            'Fecha': nd.strftime('%Y-%m-%d'),
            'Día': nd.strftime('%a'),
            'Hora (ET)': time_et,
            'Evento': name,
            'fred_id': fid,
            'Impacto': impact,
            'Anterior': prev_val,
            'Consenso Est.': cons_val,
            'Días': days_until,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values('Fecha').reset_index(drop=True)
    return df


# ============================================================
# CHART FUNCTIONS
# ============================================================
def make_chart(ind, start='2015-01-01', h=400):
    """Create a Plotly chart for one indicator."""
    _, tf_data, unit = get_indicator_data(ind['fred_id'], ind['tf'], start)
    if tf_data is None or len(tf_data) < 5:
        return None

    fig = go.Figure()

    # Area fill + line
    fig.add_trace(go.Scatter(
        x=tf_data.index, y=tf_data.values,
        fill='tozeroy',
        fillcolor='rgba(37,99,235,0.06)',
        line=dict(color=COLORS['c1'], width=2),
        name=ind['short'],
        hovertemplate='%{x|%b %d, %Y}<br><b>%{y:.2f}</b> ' + unit + '<extra></extra>'
    ))

    # MA-6
    if len(tf_data) > 6:
        ma = tf_data.rolling(6).mean()
        fig.add_trace(go.Scatter(
            x=ma.index, y=ma.values,
            line=dict(color=COLORS['gold'], width=1.5, dash='dot'),
            name='MA-6', opacity=0.7,
            hovertemplate='MA-6: %{y:.2f}<extra></extra>'
        ))

    # Last point
    lv, ld = tf_data.iloc[-1], tf_data.index[-1]
    fig.add_trace(go.Scatter(
        x=[ld], y=[lv], mode='markers+text',
        marker=dict(color=COLORS['red'], size=8, line=dict(color='white', width=2)),
        text=[f'  {lv:.2f}'], textposition='middle right',
        textfont=dict(size=11, color=COLORS['red'], family='JetBrains Mono'),
        showlegend=False, hoverinfo='skip'
    ))

    # Fed 2% target for inflation
    if ind['cat'] == 'Inflación' and ind['tf'] == 'pct12':
        fig.add_hline(y=2.0, line_dash='dot', line_color=COLORS['green'], line_width=1.5,
                      annotation_text='Fed Target 2%', annotation_position='bottom right',
                      annotation_font=dict(color=COLORS['green'], size=10))

    # Zero line for % changes
    if unit.startswith('%'):
        fig.add_hline(y=0, line_color='#e2e8f0', line_width=1)

    # COVID shading
    if pd.Timestamp('2020-02-01') >= tf_data.index.min():
        fig.add_vrect(x0='2020-02-01', x1='2020-04-01',
                      fillcolor='rgba(220,38,38,0.05)', layer='below', line_width=0)

    fig.update_layout(
        title=dict(
            text=f"<b>{ind['nombre']}</b><br>"
                 f"<span style='font-size:11px;color:#94a3b8;'>"
                 f"{ind['source']} · {ind['freq']} · "
                 f"Último: {lv:.2f} {unit} ({ld.strftime('%b %Y')})</span>",
            x=0.01, font=dict(size=13, family='DM Sans, sans-serif')
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
                bgcolor='#f1f5f9', activecolor=COLORS['primary'],
                font=dict(color='#475569', size=10),
                y=1.06
            )
        ),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', gridwidth=1,
                   title=dict(text=unit, font=dict(size=11, color='#94a3b8')),
                   zeroline=False),
        plot_bgcolor='white', paper_bgcolor='white',
        height=h,
        margin=dict(l=50, r=20, t=75, b=40),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                    font=dict(size=10, color='#64748b')),
        hovermode='x unified',
        hoverlabel=dict(bgcolor='white', font_size=12, font_family='DM Sans')
    )
    return fig


def make_comparison(indicators, title, h=380):
    """Multi-indicator comparison chart."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    palette = [COLORS['c1'], COLORS['c3'], COLORS['c4'], COLORS['c5']]

    for i, ind in enumerate(indicators):
        _, tf_data, unit = get_indicator_data(ind['fred_id'], ind['tf'])
        if tf_data is not None:
            fig.add_trace(go.Scatter(
                x=tf_data.index, y=tf_data.values,
                line=dict(color=palette[i % len(palette)], width=2),
                name=f"{ind['short']} ({unit})",
                hovertemplate=f"{ind['short']}: " + '%{y:.2f}<extra></extra>'
            ), secondary_y=(i == 1))

    fig.update_layout(
        title=dict(text=f"<b>{title}</b>", x=0.01, font=dict(size=13, family='DM Sans')),
        plot_bgcolor='white', paper_bgcolor='white',
        height=h, hovermode='x unified',
        legend=dict(orientation='h', y=1.08, font=dict(size=10)),
        margin=dict(l=50, r=50, t=60, b=40),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='#f1f5f9')
    return fig


# ============================================================
# FOMC DATA
# ============================================================
FOMC = [
    ('2025-01-29', False), ('2025-03-19', True), ('2025-05-07', False),
    ('2025-06-18', True), ('2025-07-30', False), ('2025-09-17', True),
    ('2025-10-29', False), ('2025-12-10', True),
    ('2026-01-28', False), ('2026-03-18', True), ('2026-05-06', False),
    ('2026-06-17', True), ('2026-07-29', False), ('2026-09-16', True),
    ('2026-10-28', False), ('2026-12-09', True),
]


def get_fomc():
    today = datetime.now().date()
    rows = []
    for ds, sep in FOMC:
        d = datetime.strptime(ds, '%Y-%m-%d').date()
        if d >= today:
            rows.append({
                'Fecha': d.strftime('%b %d, %Y'),
                'Tipo': '📊 Regular + SEP' if sep else 'Regular',
                'Dot Plot': '✅' if sep else '—',
                'Días': (d - today).days,
            })
    return pd.DataFrame(rows)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.divider()

    all_cats = sorted(set(i['cat'] for i in INDICADORES))
    sel_cats = st.multiselect("📂 Categorías", all_cats, default=all_cats)

    sel_impact = st.multiselect("⚡ Impacto", ['ALTO', 'MEDIO'], default=['ALTO', 'MEDIO'])

    cal_days = st.slider("📅 Días en calendario", 7, 90, 45, step=7)

    chart_start = st.selectbox(
        "📈 Historial desde",
        ['2022-01-01', '2020-01-01', '2018-01-01', '2015-01-01', '2010-01-01'],
        index=3,
        format_func=lambda x: x[:4]
    )

    st.divider()
    st.caption(f"📡 Datos: FRED (St. Louis Fed)")
    st.caption(f"🔄 Cache: 1 hora")
    st.caption(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC")
    st.caption("💡 Consenso = estimación estadística")


# ============================================================
# MAIN LAYOUT
# ============================================================

# ── HEADER ──
hdr_col1, hdr_col2 = st.columns([4, 1])
with hdr_col1:
    st.markdown("# 🏛️ US Economic Calendar")
    st.caption("Macro Research Dashboard — Datos económicos de EE.UU., consenso, históricos y monitor FOMC")
with hdr_col2:
    st.markdown("")
    st.markdown(f"**🟢 LIVE** · {datetime.now().strftime('%b %d, %Y')}")

st.divider()

# ── KPI CARDS ──
kpi_defs = [
    ('CPIAUCSL', 'pct12', '🔥 CPI YoY'),
    ('UNRATE', 'level', '👷 Desempleo'),
    ('FEDFUNDS', 'level', '🏦 Fed Funds Rate'),
    ('T10Y2Y', 'level', '📉 Curva 10Y-2Y'),
]

kpi_cols = st.columns(4)
for col, (fid, tf, label) in zip(kpi_cols, kpi_defs):
    with col:
        _, tf_data, unit = get_indicator_data(fid, tf, '2022-01-01')
        if tf_data is not None and len(tf_data) > 1:
            val = tf_data.iloc[-1]
            delta = val - tf_data.iloc[-2]
            st.metric(
                label=label,
                value=f"{val:.2f}{unit}",
                delta=f"{delta:+.2f}",
                delta_color="inverse" if fid in ('UNRATE',) else "normal"
            )
        else:
            st.metric(label=label, value="—")

st.markdown("")

# ── TABS ──
tab_cal, tab_charts, tab_fomc, tab_compare, tab_deep = st.tabs([
    "📅 Calendario",
    "📈 Gráficas",
    "🏦 FOMC",
    "🔀 Comparativos",
    "🔬 Análisis"
])


# ── TAB 1: CALENDAR ──
with tab_cal:
    st.markdown("### 📅 Próximas Publicaciones Económicas")
    st.caption("Calendario de EE.UU. con dato anterior y estimación de consenso basada en tendencia (media 3 periodos)")

    df_cal = build_calendar(cal_days)

    if not df_cal.empty:
        # Filter
        mask = df_cal['Impacto'].isin(sel_impact)
        cat_fids = [i['fred_id'] for i in INDICADORES if i['cat'] in sel_cats]
        mask &= df_cal['fred_id'].isin(cat_fids)
        df_show = df_cal[mask].copy()

        if not df_show.empty:
            # Format the countdown column with emojis
            def format_days(d):
                if d == 0:
                    return '🔴 HOY'
                elif d <= 3:
                    return f'🟠 {d}d'
                elif d <= 7:
                    return f'🟡 {d}d'
                else:
                    return f'⚪ {d}d'

            df_show['Countdown'] = df_show['Días'].apply(format_days)

            # Format impact
            def format_impact(x):
                return '🔴 ALTO' if x == 'ALTO' else '🟡 MEDIO'

            df_show['Impacto'] = df_show['Impacto'].apply(format_impact)

            # Select display columns
            display_cols = ['Fecha', 'Día', 'Hora (ET)', 'Evento', 'Impacto', 'Anterior', 'Consenso Est.', 'Countdown']
            st.dataframe(
                df_show[display_cols],
                use_container_width=True,
                hide_index=True,
                height=min(len(df_show) * 38 + 40, 600),
                column_config={
                    'Fecha': st.column_config.TextColumn('📅 Fecha', width='medium'),
                    'Día': st.column_config.TextColumn('Día', width='small'),
                    'Hora (ET)': st.column_config.TextColumn('⏰ Hora', width='small'),
                    'Evento': st.column_config.TextColumn('📊 Evento', width='large'),
                    'Impacto': st.column_config.TextColumn('⚡ Impacto', width='medium'),
                    'Anterior': st.column_config.TextColumn('📉 Anterior', width='medium'),
                    'Consenso Est.': st.column_config.TextColumn('🎯 Consenso', width='medium'),
                    'Countdown': st.column_config.TextColumn('⏳', width='small'),
                }
            )

            # Summary stats
            sc1, sc2, sc3 = st.columns(3)
            high_count = len(df_show[df_show['Impacto'].str.contains('ALTO')])
            sc1.metric("Total eventos", len(df_show))
            sc2.metric("Alto impacto", high_count)
            next_event = df_show.iloc[0]
            sc3.metric("Próximo release", f"{next_event['Evento']}", f"en {next_event['Días']} días")
        else:
            st.info("No hay eventos que coincidan con los filtros.")
    else:
        st.warning("No se pudieron cargar datos del calendario.")

    st.caption("⚠️ Para consenso de mercado en tiempo real, consultar Bloomberg / Reuters / Trading Economics.")


# ── TAB 2: CHARTS ──
with tab_charts:
    st.markdown("### 📈 Series Históricas")
    st.caption("Gráficas interactivas para cada indicador. Usa los botones 1Y/3Y/5Y/Max para cambiar el rango.")

    filtered = [i for i in INDICADORES if i['cat'] in sel_cats and i['impact'] in sel_impact]

    if not filtered:
        st.info("Selecciona al menos una categoría y nivel de impacto en el sidebar.")
    else:
        current_cat = ''
        for ind in filtered:
            cat_label = f"{ind['icon']} {ind['cat']}"
            if cat_label != current_cat:
                current_cat = cat_label
                st.markdown(f"#### {cat_label}")

            fig = make_chart(ind, start=chart_start)
            if fig:
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{ind['fred_id']}")
            else:
                st.caption(f"⚠️ {ind['short']}: datos no disponibles temporalmente")


# ── TAB 3: FOMC ──
with tab_fomc:
    st.markdown("### 🏦 Calendario FOMC")
    st.caption("Próximas reuniones del Federal Open Market Committee — decisión 14:00 ET, conferencia 14:30 ET")

    col_fomc1, col_fomc2 = st.columns([1.2, 2])

    with col_fomc1:
        df_fomc = get_fomc()
        if not df_fomc.empty:
            st.dataframe(
                df_fomc.head(10),
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Fecha': st.column_config.TextColumn('📅 Fecha', width='medium'),
                    'Tipo': st.column_config.TextColumn('Tipo', width='large'),
                    'Dot Plot': st.column_config.TextColumn('📊', width='small'),
                    'Días': st.column_config.NumberColumn('⏳ Días', width='small'),
                }
            )

            if len(df_fomc) > 0:
                next_fomc = df_fomc.iloc[0]
                st.info(f"**Próxima reunión:** {next_fomc['Fecha']} ({next_fomc['Tipo']}) — en **{next_fomc['Días']} días**")

    with col_fomc2:
        ff = fetch_fred('FEDFUNDS', '2000-01-01')
        if ff is not None:
            fig_ff = go.Figure()
            fig_ff.add_trace(go.Scatter(
                x=ff.index, y=ff.values,
                fill='tozeroy', fillcolor='rgba(15,23,42,0.06)',
                line=dict(color=COLORS['c1'], width=2),
                hovertemplate='%{x|%b %Y}: <b>%{y:.2f}%</b><extra></extra>'
            ))
            fig_ff.update_layout(
                title=dict(text="<b>Federal Funds Rate — Histórico</b>", x=0.01,
                           font=dict(size=13, family='DM Sans')),
                yaxis_title='%', plot_bgcolor='white', paper_bgcolor='white',
                height=380, margin=dict(l=50, r=20, t=50, b=40),
                hovermode='x unified', showlegend=False,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
            )
            st.plotly_chart(fig_ff, use_container_width=True)

    # 10Y-2Y Spread
    st.markdown("#### 📉 Curva de Yields — Spread 10Y vs 2Y")
    t10y2y = fetch_fred('T10Y2Y', '2000-01-01')
    if t10y2y is not None:
        fig_curve = go.Figure()
        fig_curve.add_trace(go.Scatter(
            x=t10y2y.index, y=t10y2y.values,
            fill='tozeroy',
            fillcolor=np.where(t10y2y.values < 0, 'rgba(220,38,38,0.1)', 'rgba(22,163,74,0.06)').tolist()[0],
            line=dict(color=COLORS['c1'], width=1.5),
            hovertemplate='%{x|%b %Y}: <b>%{y:.2f}%</b><extra></extra>'
        ))
        fig_curve.add_hline(y=0, line_color=COLORS['red'], line_width=1.5, line_dash='dash',
                            annotation_text='Inversión (señal recesión)',
                            annotation_font=dict(color=COLORS['red'], size=10))
        fig_curve.update_layout(
            title=dict(text="<b>Treasury Yield Spread 10Y - 2Y</b>", x=0.01,
                       font=dict(size=13, family='DM Sans')),
            yaxis_title='%', plot_bgcolor='white', paper_bgcolor='white',
            height=350, margin=dict(l=50, r=20, t=50, b=40),
            hovermode='x unified', showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
        st.plotly_chart(fig_curve, use_container_width=True)


# ── TAB 4: COMPARISONS ──
with tab_compare:
    st.markdown("### 🔀 Comparativos Multi-Indicador")
    st.caption("Cruces entre indicadores para identificar patrones macro")

    comp_col1, comp_col2 = st.columns(2)

    with comp_col1:
        inds = [i for i in INDICADORES if i['fred_id'] in ('CPIAUCSL', 'PCEPILFE')]
        fig_c1 = make_comparison(inds, 'CPI vs Core PCE — ¿Converge al 2%?')
        fig_c1.add_hline(y=2.0, line_dash='dot', line_color=COLORS['green'],
                         annotation_text='Target 2%', annotation_font=dict(color=COLORS['green'], size=10))
        st.plotly_chart(fig_c1, use_container_width=True)

    with comp_col2:
        inds2 = [i for i in INDICADORES if i['fred_id'] in ('UNRATE', 'CPIAUCSL')]
        fig_c2 = make_comparison(inds2, 'Desempleo vs Inflación (Phillips Curve)')
        st.plotly_chart(fig_c2, use_container_width=True)

    st.divider()

    # Custom comparison
    st.markdown("#### 🎛️ Comparativo personalizado")
    cc1, cc2 = st.columns(2)
    names = [i['short'] for i in INDICADORES]
    with cc1:
        sel1 = st.selectbox("Indicador 1", names, index=0)
    with cc2:
        sel2 = st.selectbox("Indicador 2", names, index=6)

    if sel1 != sel2:
        inds_custom = [i for i in INDICADORES if i['short'] in (sel1, sel2)]
        fig_custom = make_comparison(inds_custom, f'{sel1} vs {sel2}')
        st.plotly_chart(fig_custom, use_container_width=True)


# ── TAB 5: DEEP DIVE ──
with tab_deep:
    st.markdown("### 🔬 Análisis Detallado")

    sel_name = st.selectbox("Selecciona indicador", [i['short'] for i in INDICADORES], label_visibility='collapsed')
    ind = next((i for i in INDICADORES if i['short'] == sel_name), None)

    if ind:
        # Info box
        st.info(f"**{ind['nombre']}** — {ind['desc']}  \n"
                f"Fuente: {ind['source']} · Frecuencia: {ind['freq']} · FRED: `{ind['fred_id']}`")

        _, tf_data, unit = get_indicator_data(ind['fred_id'], ind['tf'], chart_start)

        if tf_data is not None and len(tf_data) > 5:
            # Stats
            s_cols = st.columns(5)
            s_cols[0].metric("Último", f"{tf_data.iloc[-1]:.2f} {unit}")
            s_cols[1].metric("Media", f"{tf_data.mean():.2f}")
            s_cols[2].metric("Máximo", f"{tf_data.max():.2f}")
            s_cols[3].metric("Mínimo", f"{tf_data.min():.2f}")
            s_cols[4].metric("Volatilidad (σ)", f"{tf_data.std():.2f}")

            # Chart
            fig_dd = make_chart(ind, start=chart_start, h=430)
            if fig_dd:
                st.plotly_chart(fig_dd, use_container_width=True, key='deep_chart')

            # Distribution
            fig_dist = go.Figure()
            fig_dist.add_trace(go.Histogram(
                x=tf_data.values, nbinsx=40,
                marker_color=COLORS['accent'], opacity=0.7,
            ))
            fig_dist.add_vline(x=tf_data.iloc[-1], line_color=COLORS['red'], line_dash='dash',
                               annotation_text=f'Actual: {tf_data.iloc[-1]:.2f}',
                               annotation_font=dict(color=COLORS['red']))
            fig_dist.add_vline(x=tf_data.mean(), line_color=COLORS['green'], line_dash='dot',
                               annotation_text=f'Media: {tf_data.mean():.2f}',
                               annotation_position='top left',
                               annotation_font=dict(color=COLORS['green']))
            fig_dist.update_layout(
                title=dict(text=f"<b>Distribución Histórica — {ind['short']}</b>", x=0.01,
                           font=dict(size=13, family='DM Sans')),
                xaxis_title=unit, yaxis_title='Frecuencia',
                plot_bgcolor='white', paper_bgcolor='white',
                height=300, margin=dict(l=50, r=20, t=50, b=40),
                showlegend=False
            )
            st.plotly_chart(fig_dist, use_container_width=True, key='deep_dist')

            # Percentile position
            current_pct = (tf_data < tf_data.iloc[-1]).mean() * 100
            st.progress(int(current_pct), text=f"Percentil actual: **{current_pct:.0f}%** (respecto al historial desde {chart_start[:4]})")
        else:
            st.warning("No se pudieron obtener datos para este indicador.")


# ── FOOTER ──
st.divider()
st.caption(
    "**US Economic Calendar** — Macro Research Dashboard · "
    "Datos: FRED (Federal Reserve Bank of St. Louis) · Sin costo · "
    "Auto-actualización al cargar (cache 1hr)  \n"
    "⚠️ El consenso es una estimación estadística, no el consenso real de mercado. "
    "No constituye asesoría de inversión."
)
