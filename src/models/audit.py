from pydantic import BaseModel, Field
from typing import Dict, Any
from src.models.receipt import ReceiptDetails


class AuditDecision(BaseModel):
    not_travel_related: bool = Field(
        description="True if the receipt is not travel-related"
    )
    amount_over_limit: bool = Field(
        description="True if the total amount exceeds $50"
    )
    math_error: bool = Field(
        description="True if there are math errors in the receipt"
    )
    handwritten_x: bool = Field(
        description="True if there is an 'X' in the handwritten notes"
    )
    reasoning: str = Field(
        description="Explanation for the audit decision"
    )
    needs_audit: bool = Field(
        description="Final determination if receipt needs auditing"
    )


class ProcessingResult(BaseModel):
    receipt_details: ReceiptDetails
    audit_decision: AuditDecision
    processing_time_ms: float
    costs: Dict[str, Any]
    processing_successful: bool = Field(
        description="True if the entire processing pipeline completed successfully"
    )
    error_message: str | None = Field(
        default=None,
        description="Error message if processing failed"
    )


class EvaluationRecord(BaseModel):
    """Holds both the correct (ground truth) and predicted audit decisions."""
    receipt_image_path: str
    correct_receipt_details: ReceiptDetails
    predicted_receipt_details: ReceiptDetails
    correct_audit_decision: AuditDecision
    predicted_audit_decision: AuditDecision