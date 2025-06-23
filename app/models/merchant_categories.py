from datetime import datetime, timezone

from sqlalchemy import DateTime, Column
from sqlmodel import Field, SQLModel, Relationship



class MerchantCategory(SQLModel, table=True):
    __tablename__ = "merchant_categories"

    category_no: int = Field(primary_key=True)
    name: str
    merchant_no: int = Field(foreign_key="merchants.merchant_no")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )
    merchant: "Merchant" = Relationship(back_populates="categories")

    transactions: list["Transaction"] = Relationship(back_populates="merchant_category")