from datetime import datetime, timezone

from sqlalchemy import DateTime, Column
from sqlmodel import Field, SQLModel, Relationship

from app.models.customers import Customer


class CustomerLocation(SQLModel, table=True):
    __tablename__ = "customer_locations"

    location_id: int = Field(primary_key=True)
    location: str
    customer_id: int = Field(foreign_key="customers.customer_no")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True)),
        default_factory=lambda: datetime.now(timezone.utc)
    )
    customer: "Customer" = Relationship(back_populates="locations")