"""
Tests for audit decision functionality.
"""
import pytest
from src.models.audit import AuditDecision, ProcessingResult
from src.models.receipt import ReceiptDetails, Location, LineItem
from src.services.audit import AuditService


@pytest.fixture
def audit_service():
    """Create audit service instance."""
    return AuditService()


@pytest.fixture
def sample_receipt_under_limit():
    """Create a receipt that doesn't need auditing."""
    return ReceiptDetails(
        merchant="Shell Gas Station",
        location=Location(city="Los Angeles", state="CA", zipcode="90001"),
        time="2024-01-01T10:00:00",
        items=[
            LineItem(
                description="Unleaded Gas",
                product_code=None,
                category="Fuel",
                item_price="4.50",
                sale_price=None,
                quantity="10",
                total="45.00"
            )
        ],
        subtotal="45.00",
        tax="3.60",
        total="48.60",
        handwritten_notes=[]
    )


@pytest.fixture
def sample_receipt_over_limit():
    """Create a receipt that needs auditing due to amount."""
    return ReceiptDetails(
        merchant="Office Supplies Store",
        location=Location(city="New York", state="NY", zipcode="10001"),
        time="2024-01-01T14:00:00",
        items=[
            LineItem(
                description="Printer Paper",
                product_code="12345",
                category="Office",
                item_price="50.00",
                sale_price=None,
                quantity="2",
                total="100.00"
            )
        ],
        subtotal="100.00",
        tax="8.00",
        total="108.00",
        handwritten_notes=[]
    )


def test_audit_decision_model():
    """Test AuditDecision model validation."""
    decision = AuditDecision(
        not_travel_related=False,
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="All criteria pass",
        needs_audit=False
    )
    
    assert decision.needs_audit is False
    assert "All criteria pass" in decision.reasoning


def test_audit_decision_needs_audit():
    """Test audit decision when criteria are violated."""
    decision = AuditDecision(
        not_travel_related=True,  # Violation
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="Non-travel expense detected",
        needs_audit=True
    )
    
    assert decision.needs_audit is True
    assert decision.not_travel_related is True


def test_processing_result_model():
    """Test ProcessingResult model."""
    receipt = ReceiptDetails(
        merchant="Test",
        location=Location(city="Test", state="CA", zipcode="12345"),
        time="2024-01-01T00:00:00",
        items=[],
        subtotal="0.00",
        tax="0.00",
        total="0.00",
        handwritten_notes=[]
    )
    
    decision = AuditDecision(
        not_travel_related=False,
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="Test",
        needs_audit=False
    )
    
    result = ProcessingResult(
        receipt_details=receipt,
        audit_decision=decision,
        processing_time_ms=100.5,
        costs={
            "extraction_cost": 0.001,
            "audit_cost": 0.0005,
            "total_cost": 0.0015
        },
        processing_successful=True,
        error_message=None
    )
    
    assert result.processing_time_ms == 100.5
    assert result.costs["total_cost"] == 0.0015
    assert result.processing_successful is True
    assert result.error_message is None


@pytest.mark.asyncio
async def test_audit_service_initialization(audit_service):
    """Test audit service is properly initialized."""
    assert audit_service is not None
    assert hasattr(audit_service, 'evaluate_receipt_for_audit')


def test_audit_criteria_logic():
    """Test various audit criteria combinations."""
    # Test 1: Travel expense under limit
    decision1 = AuditDecision(
        not_travel_related=False,
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="Travel expense under limit",
        needs_audit=False
    )
    assert not decision1.needs_audit
    
    # Test 2: Non-travel expense
    decision2 = AuditDecision(
        not_travel_related=True,
        amount_over_limit=False,
        math_error=False,
        handwritten_x=False,
        reasoning="Office supplies are not travel-related",
        needs_audit=True
    )
    assert decision2.needs_audit
    
    # Test 3: Math error detected
    decision3 = AuditDecision(
        not_travel_related=False,
        amount_over_limit=False,
        math_error=True,
        handwritten_x=False,
        reasoning="Total doesn't match line items",
        needs_audit=True
    )
    assert decision3.needs_audit
    
    # Test 4: Multiple violations
    decision4 = AuditDecision(
        not_travel_related=True,
        amount_over_limit=True,
        math_error=False,
        handwritten_x=True,
        reasoning="Multiple violations detected",
        needs_audit=True
    )
    assert decision4.needs_audit