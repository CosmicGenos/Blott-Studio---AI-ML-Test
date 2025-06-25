from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from app.models.customer_payment_methods import CustomerPaymentMethod
from app.models.customers import Customer
from app.models.merchants import Merchant
from app.models.merchant_categories import MerchantCategory
from app.models.transactions import Transaction

class PatternAnalysis:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def analyze_merchant_sells_for_category(self, merchant_id: str, category_name: str) -> Optional[Tuple[float, float]]:

        merchant_stmt = select(Merchant).where(Merchant.merchant_id == merchant_id)
        merchant_result = await self.db_session.execute(merchant_stmt)
        merchant = merchant_result.scalar_one_or_none()

        if not merchant:
            return None

        category_stmt = select(MerchantCategory).where(
            MerchantCategory.merchant_no == merchant.merchant_no,
            MerchantCategory.name == category_name
        )
        category_result = await self.db_session.execute(category_stmt)
        category = category_result.scalar_one_or_none()
        if not category:
            return None

        transaction_stmt = select(Transaction).where(
            Transaction.merchant_id == merchant.merchant_no,
            Transaction.merchant_category_id == category.category_no
        )
        transaction_result = await self.db_session.execute(transaction_stmt)
        transactions = transaction_result.scalars().all()
        if not transactions:
            return None


        amounts = [t.amount for t in transactions]
        mean = float(np.mean(amounts))
        std = float(np.std(amounts , ddof=1))
        return mean, std

    async def transaction_velocity_analysis(
            self,
            customer_id: str,
            payment_type,
            last_four: str,
            country_of_issue: str
    ) -> Optional[dict]:

        customer_stmt = select(Customer).where(Customer.customer_id == customer_id)
        customer_result = await self.db_session.execute(customer_stmt)
        customer = customer_result.scalar_one_or_none()
        if not customer:
            return None


        payment_stmt = select(CustomerPaymentMethod).where(
            CustomerPaymentMethod.customer_no == customer.customer_no,
            CustomerPaymentMethod.type == payment_type,
            CustomerPaymentMethod.last_four == last_four,
            CustomerPaymentMethod.country_of_issue == country_of_issue
        )
        payment_result = await self.db_session.execute(payment_stmt)
        payment_method = payment_result.scalar_one_or_none()
        if not payment_method:
            return None


        now = datetime.now(timezone.utc)
        one_year_ago = now - timedelta(days=365)
        transaction_stmt = select(Transaction).where(
            Transaction.customer_id == customer.customer_no,
            Transaction.customer_payment_method_id == payment_method.payment_method_id,
            Transaction.created_at >= one_year_ago
        )
        transaction_result = await self.db_session.execute(transaction_stmt)
        transactions = transaction_result.scalars().all()


        counts = {
            "last_hour": 0,
            "last_12_hours": 0,
            "last_day": 0,
            "last_month": 0,
            "total": len(transactions)
        }
        for t in transactions:
            delta = now - t.created_at
            if delta <= timedelta(hours=1):
                counts["last_hour"] += 1
            if delta <= timedelta(hours=12):
                counts["last_12_hours"] += 1
            if delta <= timedelta(days=1):
                counts["last_day"] += 1
            if delta <= timedelta(days=30):
                counts["last_month"] += 1

        return counts





