from datetime import datetime, timezone
from typing import Optional, List

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.DTO.enum import RecommendedAction, PaymentMethodType
from app.models.customers import Customer
from app.models.merchants import Merchant
from app.models.customer_payment_methods import CustomerPaymentMethod
from app.models.customer_locations import CustomerLocation
from app.models.customer_ip_addresses import CustomerIPAddress
from app.models.merchant_categories import MerchantCategory
from app.models.risk_scores import RiskScore
from app.models.notifications import Notification
from app.models.transactions import Transaction


class DataIntegration:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def save_customer_data(self, customer_id: str, is_new_customer: bool,
                                  individual_risk_score: float) -> int:
        try:
            if is_new_customer:
                customer = Customer(
                    customer_id=customer_id,
                    individual_average_risk_score=individual_risk_score,
                    transaction_count=1
                )
                self.db_session.add(customer)
                await self.db_session.flush()
                return customer.customer_no
            else:
                result = await self.db_session.execute(
                    select(Customer).where(Customer.customer_id == customer_id)
                )
                customer = result.scalar_one()
                old_total = customer.individual_average_risk_score * customer.transaction_count
                customer.transaction_count += 1
                customer.individual_average_risk_score = (
                    old_total + individual_risk_score
                ) / customer.transaction_count
                self.db_session.add(customer)
                await self.db_session.flush()
                return customer.customer_no
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def save_merchant_data(self, merchant_id: str,merchant_name:str, is_new_merchant: bool,
                                  individual_risk_score: float) -> int:
        try:
            if is_new_merchant:
                merchant = Merchant(
                    merchant_id=merchant_id,
                    individual_average_risk_score=individual_risk_score,
                    transaction_count=1,
                    merchant_name=merchant_name
                )
                self.db_session.add(merchant)
                await self.db_session.flush()
                return merchant.merchant_no
            else:
                result = await self.db_session.execute(
                    select(Merchant).where(Merchant.merchant_id == merchant_id)
                )
                merchant = result.scalar_one()
                old_total = merchant.individual_average_risk_score * merchant.transaction_count
                merchant.transaction_count += 1
                merchant.individual_average_risk_score = (
                    old_total + individual_risk_score
                ) / merchant.transaction_count
                self.db_session.add(merchant)
                await self.db_session.flush()
                return merchant.merchant_no
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def save_payment_method(self, customer_no: int, type: PaymentMethodType,
                                   last_four: str, country_of_issue: str, is_new_payment: bool) -> Optional[int]:
        try:
            if is_new_payment:
                payment_method = CustomerPaymentMethod(
                    customer_no=customer_no,
                    type=type,
                    last_four=last_four,
                    country_of_issue=country_of_issue
                )
                self.db_session.add(payment_method)
                await self.db_session.flush()
                return payment_method.payment_method_id
            else:
                result = await self.db_session.execute(
                    select(CustomerPaymentMethod)
                    .where(CustomerPaymentMethod.customer_no == customer_no)
                    .where(CustomerPaymentMethod.type == type)
                    .where(CustomerPaymentMethod.last_four == last_four)
                )
                payment_method = result.scalar_one_or_none()
                return payment_method.payment_method_id if payment_method else None
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def save_customer_location(self, customer_no: int, location: str) -> int:
        try:
            result = await self.db_session.execute(
                select(CustomerLocation)
                .where(CustomerLocation.customer_id == customer_no)
                .where(CustomerLocation.location == location)
            )
            existing_location = result.scalar_one_or_none()
            if existing_location:
                return existing_location.location_id
            else:
                new_location = CustomerLocation(
                    location=location,
                    customer_id=customer_no
                )
                self.db_session.add(new_location)
                await self.db_session.flush()
                return new_location.location_id
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def save_customer_ip_address(self, customer_no: int, ip_address: str) -> int:
        try:
            result = await self.db_session.execute(
                select(CustomerIPAddress)
                .where(CustomerIPAddress.customer_id == customer_no)
                .where(CustomerIPAddress.ip_address == ip_address)
            )
            existing_ip = result.scalar_one_or_none()
            if existing_ip:
                return existing_ip.ip_record_id
            else:
                new_ip = CustomerIPAddress(
                    customer_id=customer_no,
                    ip_address=ip_address
                )
                self.db_session.add(new_ip)
                await self.db_session.flush()
                return new_ip.ip_record_id
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def save_merchant_category(self, merchant_no: int, category_name: str) -> int:
        try:
            result = await self.db_session.execute(
                select(MerchantCategory)
                .where(MerchantCategory.merchant_no == merchant_no)
                .where(MerchantCategory.name == category_name)
            )
            existing_category = result.scalar_one_or_none()
            if existing_category:
                return existing_category.category_no
            else:
                new_category = MerchantCategory(
                    name=category_name,
                    merchant_no=merchant_no
                )
                self.db_session.add(new_category)
                await self.db_session.flush()
                return new_category.category_no
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def save_risk_score(self, transaction_no: int, score: float,
                                risk_factors: List[str], alert_type: str,
                                llm_analysis: Optional[str], customer_no: Optional[int],
                                merchant_no: Optional[int],recommendedAction:RecommendedAction) -> int:
        try:
            risk_score = RiskScore(
                transaction_id=transaction_no,
                score=score,
                risk_factors=risk_factors,
                alert_type=alert_type,
                llm_analysis=llm_analysis,
                customer_no=customer_no,
                merchant_no=merchant_no,
                decision = recommendedAction
            )
            self.db_session.add(risk_score)
            await self.db_session.flush()
            return risk_score.risk_score_id
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def save_notification(self, transaction_no: int,
                                 customer_no: int, merchant_no: int, risk_score_id: int ,customer_payment_method_id: int,
                                customer_ip_address_id:int,customer_location_id:int,
                                merchant_category_id:int) -> int:
        try:
            notification = Notification(
                transaction_id=transaction_no,
                customer_no=customer_no,
                merchant_no=merchant_no,
                risk_score_id=risk_score_id,
                customer_payment_method_id = customer_payment_method_id,
                customer_ip_address_id = customer_ip_address_id,
                customer_location_id = customer_location_id,
                merchant_category_id = merchant_category_id
            )
            self.db_session.add(notification)
            await self.db_session.flush()
            return notification.notification_id
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e

    async def save_transaction(self, transaction_id: str, amount: float,
                                currency: str, customer_no: Optional[int] = None,
                                merchant_no: Optional[int] = None, risk_score: Optional[float] = None,
                                merchant_category_id: Optional[int] = None,
                                customer_payment_method_id: Optional[int] = None) -> int:
        try:
            transaction = Transaction(
                transaction_id=transaction_id,
                amount=amount,
                currency=currency,
                created_at=datetime.now(timezone.utc),
                customer_id=customer_no,
                merchant_id=merchant_no,
                risk_score=risk_score,
                merchant_category_id=merchant_category_id,
                customer_payment_method_id=customer_payment_method_id
            )
            self.db_session.add(transaction)
            await self.db_session.flush()
            return transaction.transaction_no
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e


    async def commit_all(self):
        try:
            await self.db_session.commit()
        except SQLAlchemyError as e:
            await self.db_session.rollback()
            raise e
