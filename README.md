# Receipt Processing API

An AI-powered API for automated receipt processing and expense validation, based on eval-driven system design principles.

## Features

- **Receipt Extraction**: Automatically extract structured data from receipt images
- **Audit Decision**: Evaluate receipts against business rules to determine audit requirements
- **Cost Optimization**: Balance accuracy with processing costs using configurable models
- **RESTful API**: Simple HTTP endpoints for integration

## Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
cd receipt-processing-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### Running the API

```bash
python -m src.main
```

The API will be available at `http://localhost:8000`

### Docker Deployment

```bash
docker-compose up --build
```

## API Endpoints

### Process Receipt
```bash
POST /api/v1/receipts/process
Content-Type: multipart/form-data

file: <receipt_image>
```

### Extract Receipt Data Only
```bash
POST /api/v1/receipts/extract
Content-Type: multipart/form-data

file: <receipt_image>
```

### Audit Receipt Data
```bash
POST /api/v1/receipts/audit
Content-Type: application/json

{
  "merchant": "Store Name",
  "location": {...},
  "items": [...],
  ...
}
```

### Health Check
```bash
GET /api/v1/health/
```

## Audit Criteria

Receipts are flagged for audit if they meet ANY of these criteria:

1. **Not Travel Related**: Expenses not related to business travel
2. **Amount Over Limit**: Total exceeds $50
3. **Math Error**: Line items don't sum to the total
4. **Handwritten X**: Contains an "X" in handwritten notes

## Configuration

Key configuration options in `.env`:

- `OPENAI_MODEL_EXTRACTION`: Model for receipt data extraction
- `OPENAI_MODEL_AUDIT`: Model for audit decisions
- `AUDIT_AMOUNT_LIMIT`: Dollar threshold for audit
- `LOG_LEVEL`: Logging verbosity

## Development

### Running Tests
```bash
pytest tests/
```

### Running Evaluations
```bash
python scripts/run_eval.py
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

[Your License Here]