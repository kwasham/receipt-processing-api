"""
Receipt data models.
"""
from pydantic import BaseModel
from typing import Optional, List


class Location(BaseModel):
    """Location information from receipt."""
    city: Optional[str] = None
    state: Optional[str] = None
    zipcode: Optional[str] = None


class LineItem(BaseModel):
    """Individual line item from receipt."""
    description: Optional[str] = None
    product_code: Optional[str] = None
    category: Optional[str] = None
    item_price: Optional[str] = None
    sale_price: Optional[str] = None
    quantity: Optional[str] = None
    total: Optional[str] = None


class ReceiptDetails(BaseModel):
    """Complete receipt details."""
    merchant: Optional[str] = None
    location: Location
    time: Optional[str] = None
    items: List[LineItem]
    subtotal: Optional[str] = None
    tax: Optional[str] = None
    total: Optional[str] = None
    handwritten_notes: List[str]