"""
Custom theme configuration for PRISM Dashboard.
Modern, professional styling with dark mode support.
"""

# Custom CSS for modern PRISM dashboard
PRISM_THEME_CSS = """
<style>
/* ============================================
   PRISM Dashboard Theme - Modern Professional
   ============================================ */

/* Root variables for consistent theming */
:root {
    --prism-primary: #667eea;
    --prism-secondary: #764ba2;
    --prism-accent: #f093fb;
    --prism-success: #10b981;
    --prism-warning: #f59e0b;
    --prism-danger: #ef4444;
    --prism-dark: #1f2937;
    --prism-light: #f9fafb;
    --prism-card-bg: rgba(255, 255, 255, 0.95);
    --prism-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Page background with subtle gradient */
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e9f2 100%);
}

/* Header styling */
.stApp > header {
    background: transparent;
}

/* Main title styling */
h1 {
    background: var(--prism-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    letter-spacing: -0.5px;
}

/* Section headers */
h2 {
    color: var(--prism-dark);
    font-weight: 700;
    border-bottom: 3px solid var(--prism-primary);
    padding-bottom: 8px;
    margin-top: 2rem;
}

/* Cards / metric containers */
[data-testid="metric-container"] {
    background: var(--prism-card-bg);
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    border: 1px solid rgba(102, 126, 234, 0.1);
    /* transition removed: prevents layout jitter on every Streamlit re-render */
}

/* Metric value styling */
[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 700;
    color: var(--prism-primary);
}

/* DataFrames */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1f2937 0%, #111827 100%);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: white !important;
    -webkit-text-fill-color: white !important;
}

/* Buttons - Primary */
.stButton > button[kind="primary"] {
    background: var(--prism-gradient);
    border: none;
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    /* transform removed: scale on hover caused button-area reflow jitter */
}

/* Select boxes */
.stSelectbox > div > div {
    border-radius: 8px;
    border-color: rgba(102, 126, 234, 0.3);
}

/* Expanders */
.streamlit-expanderHeader {
    background: var(--prism-card-bg);
    border-radius: 8px;
    font-weight: 600;
}

/* Info/Warning/Error boxes */
.stAlert {
    border-radius: 10px;
    border-left-width: 5px;
}

/* Download buttons */
.stDownloadButton > button {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 600;
}

.stDownloadButton > button:hover {
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    /* transform removed: scale on hover caused button-area reflow jitter */
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: var(--prism-card-bg);
    border-radius: 8px 8px 0 0;
    padding: 10px 20px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: var(--prism-gradient);
    color: white;
}

/* Progress bar */
.stProgress > div > div > div {
    background: var(--prism-gradient);
}

/* Risk level badges */
.risk-high {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
}

.risk-medium {
    background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
}

.risk-low {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.85rem;
}

/* Dividers */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.3), transparent);
    margin: 2rem 0;
}

/* Footer area */
.stApp footer {
    visibility: hidden;
}

/* Plotly charts container */
.js-plotly-plot {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}
</style>
"""

# Color palette for charts
CHART_COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'accent': '#f093fb',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'high_risk': '#ef4444',
    'medium_risk': '#f59e0b',
    'low_risk': '#10b981',
    'gradient': ['#667eea', '#764ba2', '#f093fb'],
}

# Plotly template configuration
PLOTLY_TEMPLATE = {
    'layout': {
        'font': {'family': 'Inter, -apple-system, BlinkMacSystemFont, sans-serif'},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'colorway': ['#667eea', '#764ba2', '#f093fb', '#10b981', '#f59e0b', '#ef4444'],
        'title': {'font': {'size': 18, 'color': '#1f2937'}},
        'xaxis': {'gridcolor': 'rgba(0,0,0,0.1)', 'linecolor': 'rgba(0,0,0,0.2)'},
        'yaxis': {'gridcolor': 'rgba(0,0,0,0.1)', 'linecolor': 'rgba(0,0,0,0.2)'},
    }
}


def get_risk_color(risk_level: str) -> str:
    """Get color for risk level."""
    risk_level = str(risk_level).upper()
    if risk_level == 'HIGH':
        return CHART_COLORS['high_risk']
    elif risk_level == 'MEDIUM':
        return CHART_COLORS['medium_risk']
    else:
        return CHART_COLORS['low_risk']


def get_risk_badge_html(risk_level: str) -> str:
    """Get HTML badge for risk level."""
    risk_level = str(risk_level).upper()
    css_class = f"risk-{risk_level.lower()}"
    return f'<span class="{css_class}">{risk_level}</span>'
