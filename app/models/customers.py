from datetime import datetime, timezone
from typing import  List

from sqlalchemy import DateTime, Column
from sqlmodel import Field, SQLModel, Relationship



class Customer(SQLModel, table=True):
    __tablename__ = "customers"

    customer_no: int = Field(primary_key=True)
    customer_id: str = Field(unique=True, index=True)
    individual_average_risk_score: float = 0.0
    transaction_count: int = 0
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )


    transactions: List["Transaction"] = Relationship(back_populates="customer") # "Each customer has a list of transactions they made."
    risk_scores: List["RiskScore"] = Relationship(back_populates="customer")
    payment_methods: List["CustomerPaymentMethod"] = Relationship(back_populates="customer")
    locations: List["CustomerLocation"] = Relationship(back_populates="customer")
    ip_addresses: List["CustomerIPAddress"] = Relationship(back_populates="customer")
    notifications: List["Notification"] = Relationship(back_populates="customer")


