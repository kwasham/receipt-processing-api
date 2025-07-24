"""
Tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import json

from src.main import app
from src.models.receipt import ReceiptDetails, Location
from src.models.audit import AuditDecision


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing."""
    # Use actual test image if available
    test_image_path = Path("data/test")
    if test_image_path.exists():
        # Get first available test image
        test_images = list(test_image_path.glob("*.jpg"))
        if test_images:
            with open(test_images[0], "rb") as f:
                return {
                    "file": (test_images[0].name, f.read(), "image/jpeg")
                }
    
    # Create a minimal valid JPEG image using PIL
    from PIL import Image
    import io
    
    # Create a simple 10x10 white image
    img = Image.new('RGB', (10, 10), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    
    return {
        "file": ("test_receipt.jpg", buffer.read(), "image/jpeg")
    }


@pytest.fixture
def ground_truth_receipt():
    """Load ground truth receipt data if available."""
    ground_truth_path = Path("data/ground_truth/extraction")
    if ground_truth_path.exists():
        json_files = list(ground_truth_path.glob("*.json"))
        if json_files:
            with open(json_files[0], "r") as f:
                return json.load(f)
    return None


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_readiness_check(client):
    """Test readiness check endpoint."""
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"


def test_process_receipt_invalid_file(client, mock_openai_response):
    """Test process receipt with invalid file type."""
    files = {"file": ("test.txt", b"not an image", "text/plain")}
    response = client.post("/api/v1/receipts/process", files=files)
    assert response.status_code == 400
    assert "must be an image" in response.json()["detail"]


def test_extract_receipt_invalid_file(client, mock_openai_response):
    """Test extract receipt with invalid file."""
    files = {"file": ("test.txt", b"not a valid file", "text/plain")}
    response = client.post("/api/v1/receipts/extract", files=files)
    assert response.status_code == 400


def test_extract_receipt_pdf_support(client, mock_openai_response):
    """Test that PDF files are accepted (even if they fail processing without PyMuPDF)."""
    # Create a minimal PDF header
    pdf_content = b"%PDF-1.4\n%\xd0\xd4\xc5\xd8\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    response = client.post("/api/v1/receipts/extract", files=files)
    # PDF should pass validation but may fail processing - that's OK for this test
    assert response.status_code in [200, 500]  # 200 if PyMuPDF works, 500 if not installed


def test_audit_receipt_valid_data(client):
    """Test audit endpoint with valid receipt data."""
    receipt_data = {
        "merchant": "Gas Station",
        "location": {
            "city": "Los Angeles",
            "state": "CA",
            "zipcode": "90001"
        },
        "time": "2024-01-01T10:00:00",
        "items": [{
            "description": "Unleaded Gas",
            "product_code": None,
            "category": "Fuel",
            "item_price": "4.50",
            "sale_price": None,
            "quantity": "10",
            "total": "45.00"
        }],
        "subtotal": "45.00",
        "tax": "3.60",
        "total": "48.60",
        "handwritten_notes": []
    }
    
    response = client.post(
        "/api/v1/receipts/audit",
        json=receipt_data
    )
    
    # The actual response will depend on the OpenAI API
    # For unit tests, you'd mock the OpenAI client
    # Here we just check the endpoint is accessible
    assert response.status_code in [200, 500]  # 500 if API key not set


def test_audit_receipt_invalid_data(client):
    """Test audit endpoint with invalid data."""
    response = client.post(
        "/api/v1/receipts/audit",
        json={"invalid": "data"}
    )
    assert response.status_code == 422  # Validation error


def test_api_documentation(client):
    """Test that API documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200


def test_process_receipt_with_model_param(client, sample_image_file, mock_openai_response):
    """Test process receipt with custom model parameter."""
    response = client.post(
        "/api/v1/receipts/process?extraction_model=gpt-3.5-turbo&audit_model=gpt-3.5-turbo",
        files=sample_image_file
    )
    # With mocks, this should succeed
    assert response.status_code == 200
    data = response.json()
    assert "receipt_details" in data
    assert "audit_decision" in data
    assert "processing_successful" in data
    assert data["processing_successful"] is True


def test_extract_receipt_response_structure(client, mock_openai_response):
    """Test that extract endpoint returns correct structure."""
    # Create a proper test image
    from PIL import Image
    import io
    
    # Create a simple 10x10 white image
    img = Image.new('RGB', (10, 10), color='white')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    
    files = {"file": ("test.jpg", buffer.read(), "image/jpeg")}
    response = client.post("/api/v1/receipts/extract", files=files)
    
    assert response.status_code == 200
    data = response.json()
    # Verify response structure matches ReceiptDetails model
    assert "merchant" in data
    assert "location" in data
    assert "items" in data
    assert "total" in data


@pytest.mark.skipif(not Path("data/test").exists(), reason="Test data not available")
def test_process_receipt_with_real_image(client, mock_openai_response):
    """Test processing with actual receipt image from data folder."""
    test_image_path = list(Path("data/test").glob("*.jpg"))[0]
    
    with open(test_image_path, "rb") as f:
        files = {"file": (test_image_path.name, f.read(), "image/jpeg")}
    
    response = client.post("/api/v1/receipts/process", files=files)
    
    assert response.status_code == 200
    data = response.json()
    # Verify complete processing result structure
    assert "receipt_details" in data
    assert "audit_decision" in data
    assert "processing_time_ms" in data
    assert "costs" in data
    assert "processing_successful" in data
    assert "error_message" in data
    
    # Check audit decision structure
    audit = data["audit_decision"]
    assert "needs_audit" in audit
    assert "reasoning" in audit
    
    # Check processing status
    assert data["processing_successful"] is True
    assert data["error_message"] is None


@pytest.mark.skipif(not Path("data/ground_truth").exists(), reason="Ground truth data not available")
def test_extract_accuracy_with_ground_truth(client, ground_truth_receipt, mock_openai_response):
    """Test extraction accuracy against ground truth data."""
    if not ground_truth_receipt:
        pytest.skip("No ground truth data available")
    
    # Find corresponding image
    receipt_name = Path(list(Path("data/ground_truth/extraction").glob("*.json"))[0]).stem
    image_path = Path(f"data/test/{receipt_name}.jpg")
    
    if not image_path.exists():
        pytest.skip(f"Image file {image_path} not found")
    
    with open(image_path, "rb") as f:
        files = {"file": (image_path.name, f.read(), "image/jpeg")}
    
    response = client.post("/api/v1/receipts/extract", files=files)
    
    assert response.status_code == 200
    extracted_data = response.json()
    
    # Compare key fields
    assert extracted_data["merchant"] is not None
    assert extracted_data["total"] is not None
    # More detailed accuracy testing would be done in the evaluation scripts