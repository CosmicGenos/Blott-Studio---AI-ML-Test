from pydantic import BaseModel

from app.DTO.enum import PaymentMethodType


class Customer(BaseModel):
    id: str
    country: str
    ip_address: str

class PaymentMethod(BaseModel):
    type: PaymentMethodType
    last_four: str
    country_of_issue: str

class Merchant(BaseModel):
    id: str
    name: str
    category: str

class Transaction(BaseModel):
    transaction_id: str
    timestamp: str
    amount: float
    currency: str
    customer: Customer
    payment_method: PaymentMethod
    merchant: Merchant
