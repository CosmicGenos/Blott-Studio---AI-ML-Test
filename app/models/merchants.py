from datetime import datetime, timezone
from typing import  List

from sqlalchemy import DateTime, Column
from sqlmodel import Field, SQLModel, Relationship



class Merchant(SQLModel, table=True):
    __tablename__ = "merchants"

    merchant_no: int = Field(primary_key=True)
    merchant_id: str = Field(unique=True, index=True)
    merchant_name: str = Field(max_length=255)
    individual_average_risk_score: float = 0.0
    transaction_count: int = 0
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )

    transactions: List["Transaction"] = Relationship(back_populates="merchant")
    risk_scores: List["RiskScore"] = Relationship(back_populates="merchant")
    categories: List["MerchantCategory"] = Relationship(back_populates="merchant")
    notifications: List["Notification"] = Relationship(back_populates="merchant")