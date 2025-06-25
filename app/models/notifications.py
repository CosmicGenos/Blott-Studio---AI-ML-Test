from datetime import datetime, timezone

from sqlalchemy import DateTime, Column
from sqlmodel import Field, SQLModel, Relationship



class Notification(SQLModel, table=True):
    __tablename__ = "notifications"

    notification_id: int = Field(primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.transaction_no")
    customer_no: int = Field(foreign_key="customers.customer_no")
    merchant_no: int = Field(foreign_key="merchants.merchant_no")
    risk_score_id: int = Field(foreign_key="risk_scores.risk_score_id")
    customer_payment_method_id: int = Field(foreign_key="customer_payment_methods.payment_method_id") #here
    customer_ip_address_id: int = Field(foreign_key="customer_ip_addresses.ip_record_id")
    customer_location_id: int = Field(foreign_key="customer_locations.location_id")
    merchant_category_id: int = Field(foreign_key="merchant_categories.category_no")

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )

    transaction: "Transaction" = Relationship(back_populates="notifications")
    customer: "Customer" = Relationship(back_populates="notifications")
    merchant: "Merchant" = Relationship(back_populates="notifications")
    risk_score: "RiskScore" = Relationship(back_populates="notifications")
    customer_payment_method: "CustomerPaymentMethod" = Relationship(back_populates="notifications") #here
    customer_ip_address: "CustomerIPAddress" = Relationship(back_populates="notifications")
    customer_location: "CustomerLocation" = Relationship(back_populates="notifications")
    merchant_category: "MerchantCategory" = Relationship(back_populates="notifications")