"""
Tests for receipt extraction functionality.
"""
import pytest
from pathlib import Path
from src.models.receipt import ReceiptDetails, Location, LineItem
from src.services.extraction import ExtractionService


@pytest.fixture
def extraction_service():
    """Create extraction service instance."""
    return ExtractionService()


@pytest.fixture
def sample_receipt_image():
    """Load sample receipt image."""
    # For testing, we'll use a simple receipt structure
    # In real tests, you'd load an actual image file
    return b"fake_image_data"


def test_receipt_details_model():
    """Test ReceiptDetails model validation."""
    receipt = ReceiptDetails(
        merchant="Test Store",
        location=Location(city="Test City", state="CA", zipcode="12345"),
        time="2024-01-01T12:00:00",
        items=[
            LineItem(
                description="Test Item",
                product_code="123",
                category="Test",
                item_price="10.00",
                sale_price=None,
                quantity="1",
                total="10.00"
            )
        ],
        subtotal="10.00",
        tax="1.00",
        total="11.00",
        handwritten_notes=[]
    )
    
    assert receipt.merchant == "Test Store"
    assert receipt.location.city == "Test City"
    assert len(receipt.items) == 1
    assert receipt.total == "11.00"


def test_location_model():
    """Test Location model with optional fields."""
    # All fields provided
    location1 = Location(city="Test", state="CA", zipcode="12345")
    assert location1.city == "Test"
    
    # Some fields None
    location2 = Location(city="Test", state=None, zipcode=None)
    assert location2.city == "Test"
    assert location2.state is None


def test_line_item_model():
    """Test LineItem model validation."""
    item = LineItem(
        description="Product",
        product_code=None,
        category="Category",
        item_price="5.99",
        sale_price="4.99",
        quantity="2",
        total="9.98"
    )
    
    assert item.description == "Product"
    assert item.sale_price == "4.99"
    assert item.total == "9.98"


@pytest.mark.asyncio
async def test_extraction_service_initialization(extraction_service):
    """Test extraction service is properly initialized."""
    assert extraction_service is not None
    assert hasattr(extraction_service, 'extract_receipt_details')


def test_receipt_serialization():
    """Test receipt model serialization."""
    receipt = ReceiptDetails(
        merchant="Store",
        location=Location(city="City", state="ST", zipcode="12345"),
        time="2024-01-01T00:00:00",
        items=[],
        subtotal="0.00",
        tax="0.00",
        total="0.00",
        handwritten_notes=["Note 1", "Note 2"]
    )
    
    # Test JSON serialization
    json_data = receipt.model_dump_json()
    assert "Store" in json_data
    assert "Note 1" in json_data
    
    # Test dict conversion
    dict_data = receipt.model_dump()
    assert dict_data["merchant"] == "Store"
    assert len(dict_data["handwritten_notes"]) == 2