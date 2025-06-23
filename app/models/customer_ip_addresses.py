from datetime import datetime, timezone

from sqlalchemy import DateTime, Column
from sqlmodel import Field, SQLModel, Relationship



class CustomerIPAddress(SQLModel, table=True):
    __tablename__ = "customer_ip_addresses"

    ip_record_id: int = Field(primary_key=True)
    customer_id: int = Field(foreign_key="customers.customer_no")
    ip_address: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )
    customer: "Customer" = Relationship(back_populates="ip_addresses")