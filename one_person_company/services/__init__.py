"""
服务层 - API接入和外部服务
"""

from .search_service import SearchService
from .ecommerce_service import EcommerceService
from .finance_service import FinanceService
from .notification_service import NotificationService

__all__ = [
    'SearchService',
    'EcommerceService', 
    'FinanceService',
    'NotificationService'
]
