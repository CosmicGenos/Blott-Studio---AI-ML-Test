from datetime import datetime, timezone

from sqlalchemy import DateTime, Column
from sqlmodel import Field, SQLModel, Relationship
from app.DTO.enum import PaymentMethodType


class CustomerPaymentMethod(SQLModel, table=True):
    __tablename__ = "customer_payment_methods"

    payment_method_id: int = Field(primary_key=True)
    customer_no: int = Field(foreign_key="customers.customer_no")
    type: PaymentMethodType
    last_four: str
    country_of_issue: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )

    customer: "Customer" = Relationship(back_populates="payment_methods")
    transactions: list["Transaction"] = Relationship(back_populates="customer_payment_method")