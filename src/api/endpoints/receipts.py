"""
Receipt processing endpoints.
"""
import time
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from src.api.dependencies import (
    ExtractionServiceDep,
    AuditServiceDep,
    ValidatedImage
)
from src.models.receipt import ReceiptDetails
from src.models.audit import AuditDecision, ProcessingResult
from src.core.config import settings

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post("/process", response_model=ProcessingResult)
async def process_receipt(
    extraction_service: ExtractionServiceDep,
    audit_service: AuditServiceDep,
    file: ValidatedImage,
    extraction_model: str = Query(default=settings.DEFAULT_EXTRACTION_MODEL),
    audit_model: str = Query(default=settings.DEFAULT_AUDIT_MODEL)
) -> ProcessingResult:
    """
    Process a receipt image end-to-end.
    
    This endpoint:
    1. Extracts structured data from the receipt image
    2. Evaluates the receipt against audit criteria
    3. Returns both extraction results and audit decision
    """
    start_time = time.time()
    
    # Validate and read image
    image_data = await file.read()
    
    # Optimize image if requested and it's not a PDF
    if not (file.filename and file.filename.lower().endswith('.pdf')):
        from src.api.dependencies import optimize_image_for_ocr
        image_data = await optimize_image_for_ocr(image_data)
    
    try:
        # Extract receipt details
        extraction_start = time.time()
        receipt_details = await extraction_service.extract_receipt_details(
            image_data, file.filename or "receipt.jpg", extraction_model
        )
        extraction_time = time.time() - extraction_start
        
        # Audit receipt - FIX: use correct method name
        audit_start = time.time()
        audit_decision = await audit_service.audit_receipt(
            receipt_details, audit_model
        )
        audit_time = time.time() - audit_start
        
        # Calculate costs (simplified)
        extraction_cost = 0.001 if "mini" in extraction_model else 0.01
        audit_cost = 0.0005 if "mini" in audit_model else 0.005
        
        return ProcessingResult(
            receipt_details=receipt_details,
            audit_decision=audit_decision,
            processing_time_ms=(time.time() - start_time) * 1000,
            costs={
                "extraction_cost": extraction_cost,
                "audit_cost": audit_cost,
                "total_cost": extraction_cost + audit_cost,
                "extraction_time_ms": extraction_time * 1000,
                "audit_time_ms": audit_time * 1000
            },
            processing_successful=True,
            error_message=None
        )
    except Exception as e:
        # Return error result with minimal data
        from src.models.receipt import Location
        
        return ProcessingResult(
            receipt_details=ReceiptDetails(
                location=Location(),
                items=[],
                handwritten_notes=[]
            ),
            audit_decision=AuditDecision(
                not_travel_related=False,
                amount_over_limit=False,
                math_error=False,
                handwritten_x=False,
                reasoning=f"Processing failed: {str(e)}",
                needs_audit=True
            ),
            processing_time_ms=(time.time() - start_time) * 1000,
            costs={
                "extraction_cost": 0,
                "audit_cost": 0,
                "total_cost": 0,
                "extraction_time_ms": 0,
                "audit_time_ms": 0
            },
            processing_successful=False,
            error_message=str(e)
        )


@router.post("/extract", response_model=ReceiptDetails)
async def extract_receipt(
    extraction_service: ExtractionServiceDep,
    file: ValidatedImage,
    model: str = Query(default=settings.DEFAULT_EXTRACTION_MODEL),
    optimize_image: bool = Query(default=True, description="Optimize image for OCR")
) -> ReceiptDetails:
    """
    Extract structured data from a receipt image or PDF.
    
    Returns detailed information including merchant, items, totals, and handwritten notes.
    """
    image_data = await file.read()
    
    # Optimize image if requested and it's not a PDF
    if optimize_image and not (file.filename and file.filename.lower().endswith('.pdf')):
        from src.api.dependencies import optimize_image_for_ocr
        image_data = await optimize_image_for_ocr(image_data)
    
    return await extraction_service.extract_receipt_details(
        image_data, file.filename or "receipt.jpg", model
    )


@router.post("/audit", response_model=AuditDecision)
async def audit_receipt(
    audit_service: AuditServiceDep,
    receipt_details: ReceiptDetails,
    model: str = Query(default=settings.DEFAULT_AUDIT_MODEL)
) -> AuditDecision:
    """
    Evaluate receipt details against audit criteria.
    
    Checks for:
    - Non-travel related expenses
    - Amount over $50 limit
    - Math errors in totals
    - Presence of 'X' in handwritten notes
    """
    return await audit_service.audit_receipt(receipt_details, model)