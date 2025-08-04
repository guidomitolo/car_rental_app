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
    total_amount: Optional[Decimal] = None
    status: OrderStatus

    _db_table = 'rental_order'
    _db_fks = {
        'customer_id': Customer, 
        'vehicle_id': Vehicle
    }

    @classmethod
    def compute_amount(cls, start_date, end_date, rate):
        return_date = datetime.strptime(end_date, "%Y-%m-%d")
        pick_up_date = datetime.strptime(start_date, "%Y-%m-%d")
        diff = return_date - pick_up_date
        return (diff).days * rate

    def update(self, data):
        start_date = data.get('pick_up_date', self.pick_up_date.strftime("%Y-%m-%d"))
        end_date = data.get('return_date', self.return_date.strftime("%Y-%m-%d"))
        data['total_amount'] = self.compute_amount(start_date, end_date, self.vehicle.daily_rate)
        return super().update(data)
    
    def create(self,):
        data = super().create()
        return data
    
    @model_validator(mode='before')
    def set_total_amount(data, **kwargs) -> 'Order':
        if 'vehicle' in data:
            if 'total_amount' not in data:
                daily_rate = Vehicle.get(data['vehicle_id']).daily_rate
                data['total_amount'] = Order.compute_amount(data['pick_up_date'], data['return_date'], daily_rate)
        return data
