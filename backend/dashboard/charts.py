"""
Reusable chart components for PRISM Dashboard.
Uses Plotly for interactive, responsive visualizations.
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
import pandas as pd

from .theme import CHART_COLORS, get_risk_color


def create_risk_heatmap(risk_data: List[Dict], title: str = "Risk by Region") -> go.Figure:
    """
    Create a horizontal bar chart showing risk scores by region.
    """
    if not risk_data:
        return go.Figure()
    
    # Sort by risk score descending
    sorted_data = sorted(risk_data, key=lambda x: x.get("risk_score", 0), reverse=True)
    
    regions = [r.get("region_id", "Unknown") for r in sorted_data]
    scores = [r.get("risk_score", 0) for r in sorted_data]
    levels = [r.get("risk_level", "LOW") for r in sorted_data]
    colors = [get_risk_color(l) for l in levels]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=regions,
        x=scores,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.1)', width=1),
        ),
        text=[f"{s:.3f}" for s in scores],
        textposition='outside',
        textfont=dict(size=12, color='#1f2937'),
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Risk Score: %{x:.3f}<br>" +
            "<extra></extra>"
        ),
    ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=18, color='#1f2937', family='Inter, sans-serif'),
        ),
        xaxis=dict(
            title="Risk Score",
            range=[0, 1.05],
            gridcolor='rgba(0,0,0,0.1)',
            zeroline=False,
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
            tickfont=dict(size=12),
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=80, t=60, b=40),
        height=max(400, len(regions) * 35),
    )
    
    return fig


def create_forecast_chart(
    forecast_data: List[Dict], 
    region_id: str,
    show_actual: bool = False,
    actual_data: Optional[List[Dict]] = None
) -> go.Figure:
    """
    Create a forecast line chart with prediction bounds.
    """
    if not forecast_data:
        return go.Figure()
    
    df = pd.DataFrame(forecast_data)
    df['date'] = pd.to_datetime(df['date'])
    
    fig = go.Figure()
    
    # Prediction bounds (fill area)
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['pred_upper'],
        mode='lines',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip',
    ))
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['pred_lower'],
        mode='lines',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(102, 126, 234, 0.2)',
        name='95% Confidence',
        hoverinfo='skip',
    ))
    
    # Predicted mean
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['pred_mean'],
        mode='lines+markers',
        name='Predicted',
        line=dict(color=CHART_COLORS['primary'], width=3),
        marker=dict(size=8, color=CHART_COLORS['primary']),
        hovertemplate=(
            "<b>%{x|%Y-%m-%d}</b><br>" +
            "Predicted: %{y:.1f}<br>" +
            "<extra></extra>"
        ),
    ))
    
    # Actual values if available
    if show_actual and actual_data:
        actual_df = pd.DataFrame(actual_data)
        actual_df['date'] = pd.to_datetime(actual_df['date'])
        
        fig.add_trace(go.Scatter(
            x=actual_df['date'],
            y=actual_df['confirmed'],
            mode='lines+markers',
            name='Actual',
            line=dict(color=CHART_COLORS['success'], width=2, dash='dash'),
            marker=dict(size=6, color=CHART_COLORS['success']),
        ))
    
    fig.update_layout(
        title=dict(
            text=f"7-Day Forecast for {region_id}",
            font=dict(size=18, color='#1f2937'),
        ),
        xaxis=dict(
            title="Date",
            gridcolor='rgba(0,0,0,0.1)',
            tickformat='%Y-%m-%d',
        ),
        yaxis=dict(
            title="Predicted Cases",
            gridcolor='rgba(0,0,0,0.1)',
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
        ),
        margin=dict(l=10, r=10, t=60, b=40),
        height=400,
    )
    
    return fig


def create_model_comparison_chart(
    naive_metrics: Dict, 
    arima_metrics: Dict
) -> go.Figure:
    """
    Create a comparison chart of naive vs ARIMA model metrics.
    """
    metrics = ['MAE', 'MAPE', 'RMSE']
    naive_values = [
        naive_metrics.get('mae', 0),
        naive_metrics.get('mape', 0),
        naive_metrics.get('rmse', 0),
    ]
    arima_values = [
        arima_metrics.get('mae', 0),
        arima_metrics.get('mape', 0),
        arima_metrics.get('rmse', 0),
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Naive (Baseline)',
        x=metrics,
        y=naive_values,
        marker_color=CHART_COLORS['warning'],
        text=[f"{v:.2f}" for v in naive_values],
        textposition='outside',
    ))
    
    fig.add_trace(go.Bar(
        name='ARIMA',
        x=metrics,
        y=arima_values,
        marker_color=CHART_COLORS['primary'],
        text=[f"{v:.2f}" for v in arima_values],
        textposition='outside',
    ))
    
    fig.update_layout(
        title=dict(
            text="Model Comparison: Naive vs ARIMA",
            font=dict(size=18, color='#1f2937'),
        ),
        barmode='group',
        xaxis=dict(title="Metric"),
        yaxis=dict(title="Value (Lower is Better)", gridcolor='rgba(0,0,0,0.1)'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
        ),
        height=400,
    )
    
    return fig


def create_alert_gauge(count: int, threshold: int = 10) -> go.Figure:
    """
    Create a gauge chart showing alert count.
    """
    color = CHART_COLORS['danger'] if count >= threshold else (
        CHART_COLORS['warning'] if count >= threshold // 2 else CHART_COLORS['success']
    )
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=count,
        title={'text': "Active Alerts", 'font': {'size': 16, 'color': '#1f2937'}},
        gauge={
            'axis': {'range': [0, max(20, count + 5)]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, threshold // 2], 'color': 'rgba(16, 185, 129, 0.3)'},
                {'range': [threshold // 2, threshold], 'color': 'rgba(245, 158, 11, 0.3)'},
                {'range': [threshold, max(20, count + 5)], 'color': 'rgba(239, 68, 68, 0.3)'},
            ],
            'threshold': {
                'line': {'color': '#ef4444', 'width': 2},
                'thickness': 0.75,
                'value': threshold,
            },
        },
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_hotspot_treemap(hotspot_data: List[Dict]) -> go.Figure:
    """
    Create a treemap showing hotspot regions by case count.
    """
    if not hotspot_data:
        return go.Figure()
    
    regions = [h.get("region_id", "Unknown") for h in hotspot_data]
    values = [h.get("confirmed_sum", 0) for h in hotspot_data]
    
    fig = go.Figure(go.Treemap(
        labels=regions,
        parents=[""] * len(regions),
        values=values,
        textinfo="label+value",
        marker=dict(
            colors=values,
            colorscale='Reds',
            line=dict(width=2, color='white'),
        ),
        hovertemplate="<b>%{label}</b><br>Cases: %{value:,}<extra></extra>",
    ))
    
    fig.update_layout(
        title=dict(
            text="Hotspots by Case Count",
            font=dict(size=18, color='#1f2937'),
        ),
        margin=dict(l=10, r=10, t=50, b=10),
        height=400,
    )
    
    return fig
