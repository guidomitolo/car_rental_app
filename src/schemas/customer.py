from pydantic import Field, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime
from .base_schema import Model


class Channel(str, Enum):
    email = 'email'
    sms = 'sms'
    whatsapp = 'whatsapp'



class Customer(Model):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=10)
    contact_channel: Channel = Field(Channel.email)

    _db_table = 'customer'