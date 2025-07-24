"""
API dependencies using FastAPI's dependency injection.
"""
from typing import Annotated, List
from pathlib import Path
from fastapi import Depends, UploadFile, HTTPException, File
import io
from PIL import Image

from src.services.extraction import ExtractionService
from src.services.audit import AuditService


def get_extraction_service() -> ExtractionService:
    """Get extraction service instance."""
    return ExtractionService()


def get_audit_service() -> AuditService:
    """Get audit service instance."""
    return AuditService()


# Dependency annotations
ExtractionServiceDep = Annotated[ExtractionService, Depends(get_extraction_service)]
AuditServiceDep = Annotated[AuditService, Depends(get_audit_service)]


ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.pdf'}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB for PDFs

async def validate_file(file: UploadFile = File(...)) -> UploadFile:
    """Validate uploaded file is an allowed image or PDF format."""
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )
    
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File must be an image or PDF. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    contents = await file.read()
    await file.seek(0)  # Reset file pointer
    
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    return file

async def process_pdf_to_images(pdf_data: bytes) -> List[bytes]:
    """Convert PDF pages to images."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF processing not available. PyMuPDF package not installed."
        )
    
    pdf_document = fitz.Document(stream=pdf_data, filetype="pdf")
    images = []
    
    for page_num in range(pdf_document.page_count):
        page = pdf_document[page_num]
        # Render at 300 DPI for good OCR quality
        mat = fitz.Matrix(300/72, 300/72)
        pix = page.get_pixmap(matrix=mat)  # type: ignore
        img_data = pix.tobytes("png")
        images.append(img_data)
    
    pdf_document.close()
    return images

async def optimize_image_for_ocr(image_data: bytes, max_dimension: int = 2048) -> bytes:
    """
    Optimize image for OCR processing.
    - Resize if too large (keeping aspect ratio)
    - Convert to RGB if needed
    - Compress to reasonable quality
    """
    try:
        img = Image.open(io.BytesIO(image_data))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image file: {str(e)}"
        )
    
    # Convert RGBA to RGB if needed
    if img.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')
    
    # Resize if larger than max dimension
    if max(img.size) > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    
    # Save with optimization
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    return output.getvalue()


ValidatedImage = Annotated[UploadFile, Depends(validate_file)]