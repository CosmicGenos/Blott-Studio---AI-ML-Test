from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.DTO.ResponseDTO import NotificationDTO
from app.services.admin_notfication_service import AdminNotificationService
from ..dependancy import get_admin_notification_service

import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/notifications/high-risk", response_model=List[NotificationDTO])
async def get_high_risk_notifications(
    days_back: int = 7,
    limit: int = 100,
    service: AdminNotificationService = Depends(get_admin_notification_service)
) -> List[NotificationDTO]:
    try:
        return await service.get_high_risk_notifications(days_back, limit)
    except Exception as e:
        logger.error(f"Failed to retrieve high risk notifications: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving high risk notifications: {str(e)}"
        ) from e

@router.get("/notifications/medium-risk", response_model=List[NotificationDTO])
async def get_medium_risk_notifications(
    days_back: int = 7,
    limit: int = 100,
    service: AdminNotificationService = Depends(get_admin_notification_service)
) -> List[NotificationDTO]:
    try:
        return await service.get_medium_risk_notifications(days_back, limit)
    except Exception as e:
        logger.error(f"Failed to retrieve medium risk notifications: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving medium risk notifications: {str(e)}"
        ) from e

@router.get("/notifications/normal", response_model=List[NotificationDTO])
async def get_low_risk_notifications(
    days_back: int = 7,
    limit: int = 100,
    service: AdminNotificationService = Depends(get_admin_notification_service)
) -> List[NotificationDTO]:
    try:
        return await service.get_low_risk_notifications(days_back, limit)
    except Exception as e:
        logger.error(f"Failed to retrieve low risk notifications: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving low risk notifications: {str(e)}"
        ) from e