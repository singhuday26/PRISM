"""
PDF report generation service for PRISM using ReportLab.
Pure Python - no external GTK dependencies required.
"""
import logging
import uuid
import io
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from backend.db import get_db

logger = logging.getLogger(__name__)

# Report output directory
REPORTS_OUTPUT_DIR = Path(__file__).parent.parent.parent / "generated_reports"
REPORTS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Custom colors
PRISM_PRIMARY = colors.HexColor('#667eea')
PRISM_DARK = colors.HexColor('#5a67d8')
RISK_CRITICAL = colors.HexColor('#ef4444')
RISK_HIGH = colors.HexColor('#f97316')
RISK_MEDIUM = colors.HexColor('#eab308')
RISK_LOW = colors.HexColor('#22c55e')


def get_risk_color(level: str) -> colors.Color:
    """Get color for risk level."""
    level_colors = {
        'CRITICAL': RISK_CRITICAL,
        'HIGH': RISK_HIGH,
        'MEDIUM': RISK_MEDIUM,
        'LOW': RISK_LOW,
    }
    return level_colors.get(level.upper(), colors.grey)


def create_risk_trend_chart(risk_data: List[Dict]) -> Optional[str]:
    """
    Create a line chart showing risk score trends.
    Returns path to temporary image file.
    """
    if not risk_data:
        return None
    
    sorted_data = sorted(risk_data, key=lambda x: x.get("date", ""))
    dates = [d.get("date", "")[-5:] for d in sorted_data]  # Last 5 chars (MM-DD)
    scores = [d.get("risk_score", 0) for d in sorted_data]
    
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(dates, scores, marker='o', linewidth=2, color='#667eea')
    ax.set_xlabel('Date', fontsize=10)
    ax.set_ylabel('Risk Score', fontsize=10)
    ax.set_title('Risk Score Trend', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1)
    plt.xticks(rotation=45, ha='right', fontsize=8)
    plt.tight_layout()
    
    # Save to BytesIO
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    
    return buf


def get_styles():
    """Get custom paragraph styles for reports."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='ReportTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=PRISM_PRIMARY,
        spaceAfter=20,
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=PRISM_DARK,
        spaceBefore=20,
        spaceAfter=10,
    ))
    
    styles.add(ParagraphStyle(
        name='SubTitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
    ))
    
    return styles


def build_header(title: str, subtitle: str, styles) -> List:
    """Build report header elements."""
    elements = []
    elements.append(Paragraph(f"🔬 {title}", styles['ReportTitle']))
    elements.append(Paragraph(subtitle, styles['SubTitle']))
    elements.append(HRFlowable(width="100%", thickness=2, color=PRISM_PRIMARY))
    elements.append(Spacer(1, 20))
    return elements


def build_info_table(info_dict: Dict[str, str]) -> Table:
    """Build a styled info table for metadata."""
    data = [[k, v] for k, v in info_dict.items()]
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]))
    return table


def build_risk_table(risk_scores: List[Dict]) -> Table:
    """Build a styled risk scores table."""
    # Header row
    data = [['Region', 'Disease', 'Risk Score', 'Risk Level', 'Date']]
    
    for risk in risk_scores:
        data.append([
            risk.get('region_id', 'N/A'),
            risk.get('disease', 'N/A'),
            f"{risk.get('risk_score', 0):.3f}",
            risk.get('risk_level', 'N/A'),
            str(risk.get('date', 'N/A')),
        ])
    
    table = Table(data, colWidths=[1.2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), PRISM_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    
    # Alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f9fafb')))
    
    table.setStyle(TableStyle(style))
    return table


def build_alerts_table(alerts: List[Dict]) -> Table:
    """Build a styled alerts table."""
    data = [['Region', 'Risk Level', 'Risk Score', 'Date']]
    
    for alert in alerts[:15]:  # Limit to 15 rows
        data.append([
            alert.get('region_id', 'N/A'),
            alert.get('risk_level', 'N/A'),
            f"{alert.get('risk_score', 0):.3f}",
            str(alert.get('date', 'N/A')),
        ])
    
    table = Table(data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
    ]
    
    table.setStyle(TableStyle(style))
    return table


def generate_weekly_summary_report(start_date: str, end_date: str, disease: Optional[str] = None) -> bytes:
    """Generate a weekly summary PDF report."""
    try:
        db = get_db()
        
        query: Dict[str, Any] = {"date": {"$gte": start_date, "$lte": end_date}}
        if disease:
            query["disease"] = disease
        
        risk_scores = list(db["risk_scores"].find(query).sort("risk_score", -1).limit(15))
        alerts = list(db["alerts"].find(query).sort("created_at", -1).limit(15))
        
        high_risk_count = sum(1 for r in risk_scores if r.get("risk_score", 0) >= 0.7)
        
        # Build PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
        styles = get_styles()
        elements = []
        
        # Header
        elements.extend(build_header(
            "PRISM Weekly Summary",
            f"{start_date} to {end_date}"
        , styles))
        
        # Info table
        elements.append(build_info_table({
            "Disease Filter": disease or "All Diseases",
            "High Risk Regions": str(high_risk_count),
            "Total Alerts": str(len(alerts)),
            "Generated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        }))
        elements.append(Spacer(1, 20))
        
        # Risk scores section
        elements.append(Paragraph("📊 Top Risk Regions", styles['SectionHeading']))
        if risk_scores:
            elements.append(build_risk_table(risk_scores))
        else:
            elements.append(Paragraph("No risk data available for this period.", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Alerts section
        elements.append(Paragraph("🚨 Alerts Issued", styles['SectionHeading']))
        if alerts:
            elements.append(build_alerts_table(alerts))
        else:
            elements.append(Paragraph("No alerts issued in this period.", styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 30))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        elements.append(Paragraph(
            "Generated by PRISM (Predictive Risk Intelligence & Surveillance Model)",
            ParagraphStyle(name='Footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        ))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()
        
    except Exception as e:
        logger.error(f"Error generating weekly summary report: {e}")
        raise


def generate_region_detail_report(region_id: str, start_date: str, end_date: str, disease: Optional[str] = None) -> bytes:
    """Generate a region-specific detail PDF report."""
    try:
        db = get_db()
        
        query: Dict[str, Any] = {"region_id": region_id, "date": {"$gte": start_date, "$lte": end_date}}
        if disease:
            query["disease"] = disease
        
        risk_scores = list(db["risk_scores"].find(query).sort("date", 1))
        alerts = list(db["alerts"].find(query).sort("created_at", -1))
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
        styles = get_styles()
        elements = []
        
        # Header
        elements.extend(build_header(
            f"Region Report: {region_id}",
            f"{start_date} to {end_date}"
        , styles))
        
        # Info
        elements.append(build_info_table({
            "Region": region_id,
            "Disease Filter": disease or "All Diseases",
            "Data Points": str(len(risk_scores)),
            "Alerts": str(len(alerts)),
        }))
        elements.append(Spacer(1, 20))
        
        # Trend chart
        if risk_scores:
            chart_buf = create_risk_trend_chart(risk_scores)
            if chart_buf:
                elements.append(Paragraph("📈 Risk Score Trend", styles['SectionHeading']))
                img = Image(chart_buf, width=5*inch, height=2.5*inch)
                elements.append(img)
                elements.append(Spacer(1, 15))
        
        # Risk history
        elements.append(Paragraph("📊 Risk Score History", styles['SectionHeading']))
        if risk_scores:
            elements.append(build_risk_table(risk_scores[:10]))
        else:
            elements.append(Paragraph("No risk data available.", styles['Normal']))
        
        # Alerts
        if alerts:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("🚨 Alert History", styles['SectionHeading']))
            elements.append(build_alerts_table(alerts))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()
        
    except Exception as e:
        logger.error(f"Error generating region detail report: {e}")
        raise


def generate_disease_overview_report(disease: str, start_date: str, end_date: str) -> bytes:
    """Generate a disease overview PDF report."""
    try:
        db = get_db()
        
        query: Dict[str, Any] = {"disease": disease, "date": {"$gte": start_date, "$lte": end_date}}
        
        risk_scores = list(db["risk_scores"].find(query).sort("risk_score", -1).limit(20))
        alerts = list(db["alerts"].find(query).sort("created_at", -1).limit(20))
        
        region_set = set(r.get("region_id") for r in risk_scores if r.get("region_id"))
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
        styles = get_styles()
        elements = []
        
        # Header
        elements.extend(build_header(
            f"Disease Overview: {disease}",
            f"{start_date} to {end_date}"
        , styles))
        
        # Summary
        elements.append(build_info_table({
            "Disease": disease,
            "Affected Regions": str(len(region_set)),
            "Alerts Issued": str(len(alerts)),
            "Analysis Period": f"{start_date} to {end_date}",
        }))
        elements.append(Spacer(1, 20))
        
        # Risk by region
        elements.append(Paragraph("📊 Risk Levels by Region", styles['SectionHeading']))
        if risk_scores:
            elements.append(build_risk_table(risk_scores))
        else:
            elements.append(Paragraph(f"No risk data for {disease} in this period.", styles['Normal']))
        
        # Alerts
        if alerts:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("🚨 Alerts Issued", styles['SectionHeading']))
            elements.append(build_alerts_table(alerts))
        
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()
        
    except Exception as e:
        logger.error(f"Error generating disease overview report: {e}")
        raise


def create_report(
    report_type: str,
    region_id: Optional[str] = None,
    disease: Optional[str] = None,
    period_start: Optional[str] = None,
    period_end: Optional[str] = None
) -> str:
    """Create a report and save it to the database and filesystem."""
    try:
        report_id = f"rpt_{uuid.uuid4().hex[:12]}"
        
        if not period_end:
            period_end = datetime.utcnow().strftime("%Y-%m-%d")
        if not period_start:
            period_start = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        report_doc = {
            "report_id": report_id,
            "type": report_type,
            "region_id": region_id,
            "disease": disease,
            "period_start": period_start,
            "period_end": period_end,
            "status": "generating",
            "file_path": None,
            "file_size_bytes": None,
            "generated_at": None,
            "error": None,
            "created_at": datetime.utcnow()
        }
        
        db = get_db()
        db["reports"].insert_one(report_doc)
        
        try:
            if report_type == "weekly_summary":
                pdf_bytes = generate_weekly_summary_report(period_start, period_end, disease)
            elif report_type == "region_detail":
                if not region_id:
                    raise ValueError("region_id required for region_detail reports")
                pdf_bytes = generate_region_detail_report(region_id, period_start, period_end, disease)
            elif report_type == "disease_overview":
                if not disease:
                    raise ValueError("disease required for disease_overview reports")
                pdf_bytes = generate_disease_overview_report(disease, period_start, period_end)
            else:
                raise ValueError(f"Unknown report type: {report_type}")
            
            file_path = REPORTS_OUTPUT_DIR / f"{report_id}.pdf"
            file_path.write_bytes(pdf_bytes)
            
            db["reports"].update_one(
                {"report_id": report_id},
                {"$set": {"status": "ready", "file_path": str(file_path), 
                         "file_size_bytes": len(pdf_bytes), "generated_at": datetime.utcnow()}}
            )
            
            logger.info(f"Report generated: {report_id}")
            return report_id
            
        except Exception as e:
            db["reports"].update_one(
                {"report_id": report_id},
                {"$set": {"status": "failed", "error": str(e)}}
            )
            logger.error(f"Report generation failed: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Error creating report: {e}")
        raise


def get_report_status(report_id: str) -> Optional[Dict]:
    """Get the status of a report."""
    db = get_db()
    return db["reports"].find_one({"report_id": report_id}, {"_id": 0})


def list_reports(region_id: Optional[str] = None, disease: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """List reports with optional filters."""
    db = get_db()
    query: Dict[str, Any] = {}
    if region_id:
        query["region_id"] = region_id
    if disease:
        query["disease"] = disease
    return list(db["reports"].find(query, {"_id": 0}).sort("created_at", -1).limit(limit))


# Keep for backward compatibility with tests
def create_risk_trend_chart_base64(risk_data: List[Dict]) -> str:
    """Create chart and return as base64 string (for tests)."""
    buf = create_risk_trend_chart(risk_data)
    if not buf:
        return ""
    buf.seek(0)
    return f"data:image/png;base64,{base64.b64encode(buf.read()).decode('utf-8')}"


def render_report_template(template_name: str, context: Dict) -> str:
    """Stub for backward compatibility - ReportLab doesn't use templates."""
    # Build a simple HTML representation for testing
    return f"<html><body><h1>{context.get('title', 'Report')}</h1></body></html>"
