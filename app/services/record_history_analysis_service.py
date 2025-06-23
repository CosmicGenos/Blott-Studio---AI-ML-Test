from typing import Tuple
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.models.customers import Customer
from app.models.merchants import Merchant
from app.models.customer_payment_methods import CustomerPaymentMethod
from app.DTO.enum import PaymentMethodType


class RecordAvailability:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def check_customer_history(self, customer_id: str) -> Tuple[bool, str]:
        statement = select(Customer).where(Customer.customer_id == customer_id)
        result = await self.db_session.execute(statement)
        customer = result.first()

        if not customer:
            return True, "New customer"


        now = datetime.now(timezone.utc)
        age_days = (now - customer.created_at).days

        if age_days < 30:
            return False, f"Customer registered {age_days} days ago"
        else:
            months = age_days // 30
            remaining_days = age_days % 30
            if remaining_days > 0:
                return False, f"Customer registered {months} months and {remaining_days} days ago"
            else:
                return False, f"Customer registered {months} months ago"

    async def check_merchant_history(self, merchant_id: str) -> Tuple[bool, str]:
        statement = select(Merchant).where(Merchant.merchant_id == merchant_id)
        result = await self.db_session.execute(statement)
        merchant = result.first()

        if not merchant:
            return True, "New merchant"

        now = datetime.now(timezone.utc)
        age_days = (now - merchant.created_at).days

        if age_days < 30:
            return False, f"Merchant registered {age_days} days ago"
        else:
            months = age_days // 30
            remaining_days = age_days % 30
            if remaining_days > 0:
                return False, f"Merchant registered {months} months and {remaining_days} days ago"
            else:
                return False, f"Merchant registered {months} months ago"

    async def check_payment_method(self, customer_id: str, payment_type: PaymentMethodType,
                                   last_four: str, country_of_issue: str) -> Tuple[bool, str]:

        customer_statement = select(Customer).where(Customer.customer_id == customer_id)
        customer_result = await self.db_session.execute(customer_statement)
        customer = customer_result.first()

        if not customer:
            return True, "New customer with new payment method"


        payment_statement = select(CustomerPaymentMethod).where(
            CustomerPaymentMethod.customer_no == customer.customer_no,
            CustomerPaymentMethod.type == payment_type,
            CustomerPaymentMethod.last_four == last_four,
            CustomerPaymentMethod.country_of_issue == country_of_issue
        )

        payment_result = await self.db_session.execute(payment_statement)
        payment_method = payment_result.first()

        now = datetime.now(timezone.utc)
        age_days = (now - payment_method.created_at).days

        if age_days < 30:
            return False, f"Payment method used {age_days} days ago"
        else:
            months = age_days // 30
            remaining_days = age_days % 30
            if remaining_days > 0:
                return False, f"Payment method used {months} months and {remaining_days} days ago"
            else:
                return False, f"Payment method used {months} months ago"

    async def get_merchant_risk_and_transaction_count(self, merchant_id: str) -> tuple[float, int] | None:
        statement = select(Merchant).where(Merchant.merchant_id == merchant_id)
        result = await self.db_session.execute(statement)
        merchant = result.scalar_one_or_none()
        if merchant:
            return merchant.individual_average_risk_score, merchant.transaction_count
        return None



