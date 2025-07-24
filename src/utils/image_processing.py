"""
Image processing utilities for receipt images.
"""
import base64
import mimetypes
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
import io


def encode_image_to_base64(image_data: bytes, filename: str) -> str:
    """
    Encode image data to base64 data URI.
    
    Args:
        image_data: Raw image bytes
        filename: Original filename to determine MIME type
        
    Returns:
        Base64 encoded data URI
    """
    # Try to determine MIME type from filename
    mime_type, _ = mimetypes.guess_type(filename)
    
    # If we can't determine from filename, try to detect from image data
    if not mime_type or not mime_type.startswith('image/'):
        try:
            # Try to detect image format from the actual data
            img = Image.open(io.BytesIO(image_data))
            image_format = img.format.lower() if img.format else None
            
            if image_format == 'jpeg' or image_format == 'jpg':
                mime_type = "image/jpeg"
            elif image_format == 'png':
                mime_type = "image/png"
            elif image_format == 'gif':
                mime_type = "image/gif"
            elif image_format == 'webp':
                mime_type = "image/webp"
            else:
                mime_type = "image/jpeg"  # Default fallback
        except Exception:
            # If we can't detect, default to JPEG
            mime_type = "image/jpeg"
    
    # Ensure it's a valid image MIME type
    if not mime_type.startswith('image/'):
        mime_type = "image/jpeg"
    
    b64_image = base64.b64encode(image_data).decode("utf-8")
    return f"data:{mime_type};base64,{b64_image}"


def validate_image(image_data: bytes) -> Tuple[bool, Optional[str]]:
    """
    Validate image data.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Try to open the image
        img = Image.open(io.BytesIO(image_data))
        
        # Check image size
        width, height = img.size
        if width * height > 20_000_000:  # 20 megapixels
            return False, "Image is too large (max 20MP)"
        
        # Check file size
        if len(image_data) > 20 * 1024 * 1024:  # 20MB
            return False, "File size is too large (max 20MB)"
        
        return True, None
        
    except Exception as e:
        return False, f"Invalid image format: {str(e)}"


def preprocess_image(image_data: bytes) -> bytes:
    """
    Preprocess image for better OCR results.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Processed image bytes
    """
    try:
        # Open image
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        max_dimension = 2048
        if max(img.size) > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=95)
        return output.getvalue()
        
    except Exception:
        # Return original if preprocessing fails
        return image_data