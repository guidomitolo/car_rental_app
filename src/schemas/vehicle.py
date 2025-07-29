from pydantic import Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum
from .base_schema import Model


class VehicleType(str, Enum):
    """Enum for vehicle types."""
    SEDAN = 'Sedan'
    SUV = 'SUV'
    VAN = 'VAN'

class Vehicle(Model):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    manufacturer: str = Field(..., max_length=50)
    model: str = Field(..., max_length=50)
    type: VehicleType = Field(VehicleType.SUV)
    year: int = Field(..., ge=1900, le=datetime.now().year + 1)
    license_plate: Optional[str] = Field(None, max_length=20)
    daily_rate: Decimal = Field(Decimal('0.00'), ge=0, decimal_places=2)
    is_available: bool = Field(True)

    _db_table = 'vehicle'
