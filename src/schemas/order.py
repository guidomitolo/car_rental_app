from pydantic import model_validator
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from .base_schema import Model
from .customer import Customer
from .vehicle import Vehicle


class OrderStatus(str, Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class Order(Model):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    customer_id: int
    vehicle_id: int
    pick_up_date: date
    return_date: date
    total_amount: Optional[Decimal]
    status: OrderStatus

    _db_table = 'rental_order'
    _db_fks = {
        'customer_id': Customer, 
        'vehicle_id': Vehicle
    }

    def update(self, data):
        return super().update(data)
    
    def create(self,):
        data = super().create()
        return data
    
    @model_validator(mode='before')
    def check_total_amount(self) -> 'Order':
        if 'total_amount' not in self:
            return_date = datetime.strptime(self['return_date'], "%Y-%m-%d")
            pick_up_date = datetime.strptime(self['pick_up_date'], "%Y-%m-%d")
            self['customer'] = Customer.get(self['customer_id'])
            self['vehicle'] = Vehicle.get(self['vehicle_id'])
            diff = return_date - pick_up_date
            self['total_amount'] = self['vehicle'].daily_rate * (diff).days
        return self
