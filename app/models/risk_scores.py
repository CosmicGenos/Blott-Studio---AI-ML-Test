from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import Column, String, DateTime
from sqlmodel import Field, SQLModel, Relationship
from app.DTO.enum import RecommendedAction
from sqlalchemy.dialects import postgresql

class RiskScore(SQLModel, table=True):
    __tablename__ = "risk_scores"

    risk_score_id: int = Field(primary_key=True)
    transaction_id: int = Field(foreign_key="transactions.transaction_no")
    score: float
    decision: RecommendedAction
    risk_factors: List[str] = Field(sa_column=Column(postgresql.ARRAY(String())))
    llm_analysis: Optional[str] = None
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )
    customer_no: Optional[int] = Field(foreign_key="customers.customer_no")
    merchant_no: Optional[int] = Field(foreign_key="merchants.merchant_no")

    # transaction: "Transaction" = Relationship(back_populates="risk_score")
    customer: Optional["Customer"] = Relationship(back_populates="risk_scores")
    merchant: Optional["Merchant"] = Relationship(back_populates="risk_scores")
    notifications: Optional["Notification"] = Relationship(back_populates="risk_score")