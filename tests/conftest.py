"""
Test configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_data_dir():
    """Get test data directory."""
    return Path(__file__).parent.parent / "data" / "test"


@pytest.fixture
def mock_openai_response(monkeypatch):
    """Mock OpenAI API responses."""
    from src.models.receipt import ReceiptDetails, Location, LineItem
    from src.models.audit import AuditDecision
    
    async def mock_extract_receipt_details(self, image_data, filename, model="gpt-4o-mini"):
        """Mock extraction service method."""
        return ReceiptDetails(
            merchant="Test Store",
            location=Location(city="Test City", state="CA", zipcode="12345"),
            time="2024-01-01T12:00:00",
            items=[],
            subtotal="10.00",
            tax="1.00",
            total="11.00",
            handwritten_notes=[]
        )
    
    async def mock_evaluate_receipt_for_audit(self, receipt_details, model="gpt-4o-mini"):
        """Mock audit service method."""
        return AuditDecision(
            not_travel_related=False,
            amount_over_limit=False,
            math_error=False,
            handwritten_x=False,
            reasoning="Test reasoning",
            needs_audit=False
        )
    
    # Mock the service methods directly
    monkeypatch.setattr("src.services.extraction.ExtractionService.extract_receipt_details", 
                       mock_extract_receipt_details)
    monkeypatch.setattr("src.services.audit.AuditService.evaluate_receipt_for_audit", 
                       mock_evaluate_receipt_for_audit)