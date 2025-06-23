from typing import Optional

from sqlalchemy import DateTime, Column
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime, timezone


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    transaction_no: int = Field(primary_key=True)
    transaction_id: str = Field(unique=True, index=True)
    amount: float
    currency: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )

    customer_id: Optional[int] = Field(foreign_key="customers.customer_no")
    merchant_id: Optional[int] = Field(foreign_key="merchants.merchant_no")
    risk_score: float
    merchant_category_id : Optional[int] = Field(foreign_key="merchant_categories.category_no")
    customer_payment_method_id: Optional[int] = Field(foreign_key="customer_payment_methods.payment_method_id")

    customer: Optional["Customer"] = Relationship(back_populates="transactions") #"Each transaction knows which customer made it."
    merchant: Optional["Merchant"] = Relationship(back_populates="transactions")
    # risk_score: Optional["RiskScore"] = Relationship(back_populates="transactions")
    merchant_category: Optional["MerchantCategory"] = Relationship(back_populates="transactions")
    customer_payment_method: Optional["CustomerPaymentMethod"] = Relationship(back_populates="transactions")
    notifications: Optional["Notification"] = Relationship(back_populates="transaction")