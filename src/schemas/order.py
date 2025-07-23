from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from .base_schema import Model


class OrderStatus(str, Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class Order(Model):
    id: int = Field(..., description="Unique identifier for the rental order.")
    created_at: datetime = Field(..., description="Timestamp when the rental order was created.")
    customer_id: int = Field(..., description="ID of the customer who placed the order.")
    vehicle_id: int = Field(..., description="ID of the vehicle rented.")
    pick_up_date: date = Field(..., description="Date when the vehicle is picked up.")
    return_date: date = Field(..., description="Date when the vehicle is returned.")
    total_amount: Decimal = Field(..., ge=0, decimal_places=2, description="Total amount for the rental order.")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Current status of the rental order.")

    class Meta:
        __db_table__ = 'rental_order'

    def calculate_rate(self, start, end, rate):
        pass
        # start_date = datetime.strptime(start, "%Y-%m-%d")
        # end_date = datetime.strptime(end, "%Y-%m-%d")
        # diff = end_date - start_date
        # total = rate * (diff).days
        # return total

