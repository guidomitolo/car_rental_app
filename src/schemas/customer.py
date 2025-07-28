from pydantic import Field
from typing import Optional
from enum import Enum
from datetime import datetime
from .base_schema import Model


class Channel(str, Enum):
    email = 'email'
    sms = 'sms'
    whatsapp = 'whatsapp'



class Customer(Model):
    id: int = None
    created_at: datetime = None
    first_name: str = Field(..., max_length=50, description="Customer's first name.")
    last_name: str = Field(..., max_length=50, description="Customer's last name.")
    email: str = Field(..., max_length=100, description="Unique email address of the customer.")
    phone: Optional[str] = Field(None, max_length=20, description="Customer's phone number.")
    address: Optional[str] = Field(None, max_length=255, description="Customer's street address.")
    city: Optional[str] = Field(None, max_length=100, description="Customer's city.")
    state: Optional[str] = Field(None, max_length=100, description="Customer's state.")
    state: Optional[str] = Field(None, max_length=100, description="Customer's state.")
    zip_code: Optional[str] = Field(None, max_length=10, description="Customer's zip code.")
    contact_channel: Channel = Field(Channel.email, description="Customer desired contact channel")

    class Meta:
        __db_table__ = 'customer'