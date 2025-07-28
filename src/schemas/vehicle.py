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
    id: int = None
    created_at: datetime = None
    manufacturer: str
    model: str
    type: VehicleType
    year: int = Field(..., ge=1900, le=datetime.now().year + 1)
    license_plate: Optional[str] = Field(None, max_length=20)
    daily_rate: Decimal = Field(Decimal('0.00'), ge=0, decimal_places=2)
    is_available: bool = Field(True)

    class Meta:
        __db_table__ = 'vehicle'
