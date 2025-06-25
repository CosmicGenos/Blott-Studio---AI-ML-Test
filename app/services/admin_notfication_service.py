from datetime import datetime, timezone, timedelta
from typing import List

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.DTO.ResponseDTO import NotificationDTO, RiskScoreDTO
from app.DTO.RequestDTO import Transaction, Customer, Merchant, PaymentMethod
from app.models.notifications import Notification
# from app.models.transactions import Transaction as TransactionModel
from app.models.risk_scores import RiskScore
from app.DTO.enum import RecommendedAction


class AdminNotificationService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_notifications_by_decision(
            self,
            decision_type: RecommendedAction,
            days_back: int = 7,
            limit: int = 100
    ) -> List[NotificationDTO]:

        since_date = datetime.now(timezone.utc) - timedelta(days=days_back)

        query = (
            select(Notification)
            .join(RiskScore, Notification.risk_score_id == RiskScore.risk_score_id)
            .filter(RiskScore.decision == decision_type)
            .filter(Notification.created_at >= since_date)
            .order_by(desc(Notification.created_at))
            .limit(limit)
            .options(
                selectinload(Notification.risk_score),
                selectinload(Notification.transaction),
                selectinload(Notification.customer),
                selectinload(Notification.merchant),
                selectinload(Notification.customer_payment_method),
                selectinload(Notification.customer_location),
                selectinload(Notification.customer_ip_address),
                selectinload(Notification.merchant_category)
            )
        )

        result = await self.db_session.execute(query)
        notifications = result.scalars().all()

        return [ self.format_notification_dto(notification) for notification in notifications]

    async def get_high_risk_notifications(self, days_back: int = 7, limit: int = 100) -> List[NotificationDTO]:

        notifications = await self.get_notifications_by_decision(
            RecommendedAction.BLOCK,
            days_back,
            limit
        )

        for notification in notifications:
            notification.alert_type = "high_risk_transaction"

        return notifications

    async def get_medium_risk_notifications(self, days_back: int = 7, limit: int = 100) -> List[NotificationDTO]:

        notifications = await self.get_notifications_by_decision(
            RecommendedAction.REVIEW,
            days_back,
            limit
        )

        for notification in notifications:
            notification.alert_type = "suspicious_transaction"

        return notifications

    async def get_low_risk_notifications(self, days_back: int = 7, limit: int = 100) -> List[NotificationDTO]:

        notifications = await self.get_notifications_by_decision(
            RecommendedAction.ALLOW,
            days_back,
            limit
        )

        for notification in notifications:
            notification.alert_type = "normal_transaction"

        return notifications

    def format_notification_dto(self, notification: Notification) -> NotificationDTO:


        transaction_dto = Transaction(
            transaction_id=notification.transaction.transaction_id,
            timestamp=notification.transaction.created_at.isoformat(),
            amount=notification.transaction.amount,
            currency=notification.transaction.currency,
            customer=Customer(
                id=notification.customer.customer_id,
                country=notification.customer_location.location,
                ip_address=notification.customer_ip_address.ip_address
            ),
            payment_method=PaymentMethod(
                type=notification.customer_payment_method.type,
                last_four=notification.customer_payment_method.last_four,
                country_of_issue=notification.customer_payment_method.country_of_issue
            ),
            merchant=Merchant(
                id=notification.merchant.merchant_id,
                name=notification.merchant.merchant_name,
                category=notification.merchant_category.name
            )
        )


        risk_score_dto = RiskScoreDTO(
            risk_score=notification.risk_score.score,
            risk_factors=notification.risk_score.risk_factors,
            reasoning=notification.risk_score.llm_analysis or ""
        )


        alert_type = "normal_transaction"
        if notification.risk_score.decision == RecommendedAction.BLOCK:
            alert_type = "high_risk_transaction"
        elif notification.risk_score.decision == RecommendedAction.REVIEW:
            alert_type = "suspicious_transaction"

        return NotificationDTO(
            alert_type=alert_type,
            transaction=transaction_dto,
            risk_score=risk_score_dto
        )


