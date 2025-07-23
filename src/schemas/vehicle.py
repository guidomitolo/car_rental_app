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
    id: int = Field(..., description="Unique identifier for the vehicle.")
    created_at: datetime = Field(..., description="Timestamp when the vehicle record was created.")
    manufacturer: str = Field(..., description="Manufacturer of the vehicle.")
    model: str = Field(..., description="Model of the vehicle.")
    type: VehicleType = Field(VehicleType.SEDAN, description="Type of the vehicle (Sedan, SUV, VAN).")
    year: int = Field(..., ge=1900, le=datetime.now().year + 1, description="Manufacturing year of the vehicle.")
    license_plate: Optional[str] = Field(None, max_length=20, description="Unique license plate of the vehicle.")
    daily_rate: Decimal = Field(Decimal('0.00'), ge=0, decimal_places=2, description="Daily rental rate for the vehicle.")
    is_available: bool = Field(True, description="Availability status of the vehicle.")

    class Meta:
        __db_table__ = 'vehicle'
