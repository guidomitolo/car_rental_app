from pydantic import Field
from typing import Optional
from datetime import datetime
from .base_schema import Model


class Customer(Model):
    id: int = Field(..., description="Unique identifier for the customer.")
    created_at: datetime = Field(..., description="Timestamp when the customer record was created.")
    first_name: str = Field(..., max_length=50, description="Customer's first name.")
    last_name: str = Field(..., max_length=50, description="Customer's last name.")
    email: str = Field(..., max_length=100, description="Unique email address of the customer.")
    phone: Optional[str] = Field(None, max_length=20, description="Customer's phone number.")
    address: Optional[str] = Field(None, max_length=255, description="Customer's street address.")
    city: Optional[str] = Field(None, max_length=100, description="Customer's city.")
    state: Optional[str] = Field(None, max_length=100, description="Customer's state.")
    zip_code: Optional[str] = Field(None, max_length=10, description="Customer's zip code.")

    class Meta:
        __db_table__ = 'customer'

    

    

