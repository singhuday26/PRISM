"""
Report generation API routes.
"""
import logging
from typing import Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.services.reports import (
    create_report,
    get_report_status,
    list_reports
)

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class GenerateReportRequest(BaseModel):
    """Request body for generating a report."""
    type: str = Field(..., description="Report type: weekly_summary, region_detail, or disease_overview")
    region_id: Optional[str] = Field(None, description="Region ID (required for region_detail)")
    disease: Optional[str] = Field(None, description="Disease filter")
    period_start: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    period_end: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")


class GenerateReportResponse(BaseModel):
    """Response for report generation request."""
    report_id: str
    status: str
    estimated_time_seconds: int = 10


class ReportStatusResponse(BaseModel):
    """Response with report status."""
    report_id: str
    type: str
    status: str
    download_url: Optional[str] = None
    generated_at: Optional[str] = None
    error: Optional[str] = None


class ReportListResponse(BaseModel):
    """Response with list of reports."""
    reports: list
    count: int


@router.post("/generate", response_model=GenerateReportResponse, status_code=status.HTTP_202_ACCEPTED)
def generate_report(request: GenerateReportRequest):
    """
    Generate a PDF report.
    
    Args:
        request: Report generation parameters
        
    Returns:
        Report ID and status
    """
    try:
        # Validate report type
        valid_types = ["weekly_summary", "region_detail", "disease_overview"]
        if request.type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid report type. Must be one of: {valid_types}"
            )
        
        # Validate region_detail requirements
        if request.type == "region_detail" and not request.region_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="region_id is required for region_detail reports"
            )
        
        # Validate disease_overview requirements
        if request.type == "disease_overview" and not request.disease:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="disease is required for disease_overview reports"
            )
        
        # Create report
        report_id = create_report(
            report_type=request.type,
            region_id=request.region_id,
            disease=request.disease,
            period_start=request.period_start,
            period_end=request.period_end
        )
        
        logger.info(f"Report generation started: {report_id}")
        
        return GenerateReportResponse(
            report_id=report_id,
            status="generating",
            estimated_time_seconds=10
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating report generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/{report_id}", response_model=ReportStatusResponse)
def get_report(report_id: str):
    """
    Get report status and metadata.
    
    Args:
        report_id: Report ID
        
    Returns:
        Report status
    """
    try:
        report = get_report_status(report_id)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Build response
        response = ReportStatusResponse(
            report_id=report["report_id"],
            type=report["type"],
            status=report["status"],
            error=report.get("error")
        )
        
        # Add download URL if ready
        if report["status"] == "ready":
            response.download_url = f"/reports/{report_id}/download"
            if report.get("generated_at"):
                response.generated_at = report["generated_at"].isoformat() if isinstance(report["generated_at"], datetime) else report["generated_at"]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting report status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get report status: {str(e)}"
        )


@router.get("/{report_id}/download")
def download_report(report_id: str):
    """
    Download a generated PDF report.
    
    Args:
        report_id: Report ID
        
    Returns:
        PDF file
    """
    try:
        report = get_report_status(report_id)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        if report["status"] != "ready":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Report not ready. Status: {report['status']}"
            )
        
        file_path = report.get("file_path")
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Report file path not found"
            )
        
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=f"{report_id}.pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download report: {str(e)}"
        )


@router.get("/list", response_model=ReportListResponse)
def list_all_reports(
    region_id: Optional[str] = Query(None, description="Filter by region"),
    disease: Optional[str] = Query(None, description="Filter by disease"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results")
):
    """
    List generated reports with optional filters.
    
    Args:
        region_id: Filter by region
        disease: Filter by disease
        limit: Maximum results
        
    Returns:
        List of reports
    """
    try:
        reports = list_reports(
            region_id=region_id,
            disease=disease,
            limit=limit
        )
        
        return ReportListResponse(
            reports=reports,
            count=len(reports)
        )
        
    except Exception as e:
        logger.error(f"Error listing reports: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reports: {str(e)}"
        )
