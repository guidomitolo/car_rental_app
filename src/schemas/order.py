from pydantic import Field, model_validator
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from .base_schema import Model
from .customer import Customer
from .vehicle import Vehicle

class OrderStatus(str, Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class Order(Model):
    id: int = Field(None, description="Unique identifier for the rental order.")
    created_at: datetime|None = Field(None, description="Timestamp when the rental order was created.")
    customer_id: int = Field(..., description="ID of the customer who placed the order.")
    vehicle_id: int = Field(..., description="ID of the vehicle rented.")
    pick_up_date: date = Field(..., description="Date when the vehicle is picked up.")
    return_date: date = Field(..., description="Date when the vehicle is returned.")
    total_amount: Decimal = Field(None, description="Total amount for the rental order.")
    status: OrderStatus = Field(OrderStatus.PENDING, description="Current status of the rental order.")

    class Meta:
        __db_table__ = 'rental_order'
        __db_fks__ = {
            'customer_id': Customer, 
            'vehicle_id': Vehicle
        }

    def update(self, data):
        return super().update(data)
    
    def create(self,):
        data = super().create()
        return data
    
    @model_validator(mode='after')
    def check_total_amount(self):
        diff = self.return_date - self.pick_up_date
        self.total_amount = self.vehicle.daily_rate * (diff).days
