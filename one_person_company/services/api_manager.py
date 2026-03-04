"""
API管理器 - 统一管理所有外部API接入
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .search_service import SearchService
from .ecommerce_service import EcommerceService
from .finance_service import FinanceService
from .notification_service import NotificationService

logger = logging.getLogger(__name__)


class APIManager:
    """
    统一API管理器
    负责初始化和管理所有外部服务
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or Path(__file__).parent.parent / 'config' / 'api_keys.yaml'
        self.config = self._load_config()
        
        # 初始化各服务
        self.search: SearchService = None
        self.ecommerce: EcommerceService = None
        self.finance: FinanceService = None
        self.notification: NotificationService = None
        
        self._init_services()
        
    def _load_config(self) -> Dict:
        """加载API配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info("✅ API配置加载成功")
                return config
        except FileNotFoundError:
            logger.warning("⚠️ API配置文件不存在，使用默认配置")
            return {}
        except Exception as e:
            logger.error(f"❌ 加载API配置失败: {e}")
            return {}
    
    def _init_services(self) -> None:
        """初始化所有服务"""
        
        # 1. 搜索服务
        search_config = self.config.get('search', {})
        brave_key = search_config.get('brave_api_key', '')
        self.search = SearchService(api_key=brave_key)
        logger.info(f"✅ 搜索服务已初始化 (Brave API: {'已配置' if brave_key else '未配置'})")
        
        # 2. 电商服务
        ecommerce_config = self.config.get('ecommerce', {})
        self.ecommerce = EcommerceService(config=ecommerce_config)
        logger.info("✅ 电商服务已初始化")
        
        # 3. 金融服务
        finance_config = self.config.get('finance', {})
        self.finance = FinanceService(config=finance_config)
        logger.info("✅ 金融服务已初始化")
        
        # 4. 通知服务
        notification_config = self.config.get('notification', {}).get('email', {})
        self.notification = NotificationService(config=notification_config)
        logger.info("✅ 通知服务已初始化")
    
    def get_service_status(self) -> Dict:
        """获取所有服务状态"""
        return {
            "timestamp": datetime.now().isoformat(),
            "services": {
                "search": {
                    "status": "active" if self.search else "inactive",
                    "provider": "Brave Search"
                },
                "ecommerce": {
                    "status": "active" if self.ecommerce else "inactive",
                    "platforms": ["抖音", "1688", "小红书"]
                },
                "finance": {
                    "status": "active" if self.finance else "inactive",
                    "markets": ["A股", "港股", "美股"]
                },
                "notification": {
                    "status": "active" if self.notification else "inactive",
                    "channels": ["QQ邮箱"]
                }
            }
        }
    
    def test_all_services(self) -> Dict:
        """测试所有服务连接"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # 测试搜索
        try:
            search_result = self.search.search_web("test", count=1)
            results["tests"]["search"] = {
                "status": "pass" if search_result.get("status") == "success" else "fail",
                "message": search_result.get("message", "OK")
            }
        except Exception as e:
            results["tests"]["search"] = {"status": "fail", "message": str(e)}
        
        # 测试金融
        try:
            finance_result = self.finance.get_a_stock_realtime("600519")
            results["tests"]["finance"] = {
                "status": "pass" if finance_result.get("status") == "success" else "fail",
                "message": finance_result.get("message", "OK")
            }
        except Exception as e:
            results["tests"]["finance"] = {"status": "fail", "message": str(e)}
        
        # 通知服务需要配置后才能测试
        email_auth = self.config.get('notification', {}).get('email', {}).get('auth_code', '')
        results["tests"]["notification"] = {
            "status": "configured" if email_auth else "not_configured",
            "message": "邮箱授权码已配置" if email_auth else "请配置QQ邮箱授权码"
        }
        
        return results
    
    # ==================== 便捷方法 ====================
    
    def search_market(self, keyword: str) -> Dict:
        """市场搜索"""
        return self.search.search_web(keyword)
    
    def search_product(self, product_name: str) -> Dict:
        """产品搜索"""
        return self.search.search_products(product_name)
    
    def analyze_product_opportunity(self, product_name: str) -> Dict:
        """分析产品机会"""
        return self.ecommerce.analyze_product_opportunity(product_name)
    
    def get_stock_data(self, stock_code: str, market: str = "A") -> Dict:
        """获取股票数据"""
        if market == "A":
            return self.finance.get_a_stock_realtime(stock_code)
        elif market == "HK":
            return self.finance.get_hk_stock_realtime(stock_code)
        elif market == "US":
            return self.finance.get_us_stock_realtime(stock_code)
        else:
            return {"status": "error", "message": f"不支持的市场: {market}"}
    
    def get_watchlist(self) -> Dict:
        """获取关注股票"""
        return self.finance.get_watchlist_status()
    
    def send_report(self, report: str, to: str = None) -> Dict:
        """发送报告"""
        return self.notification.send_daily_report(report, to)
    
    def send_alert(self, alert_type: str, message: str) -> Dict:
        """发送告警"""
        return self.notification.send_alert(alert_type, message)


# 全局实例
_api_manager: APIManager = None


def get_api_manager() -> APIManager:
    """获取API管理器单例"""
    global _api_manager
    if _api_manager is None:
        _api_manager = APIManager()
    return _api_manager


# 测试
if __name__ == "__main__":
    import json
    
    manager = APIManager()
    
    print("=" * 60)
    print("服务状态")
    print("=" * 60)
    print(json.dumps(manager.get_service_status(), ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("服务测试")
    print("=" * 60)
    print(json.dumps(manager.test_all_services(), ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 60)
    print("测试产品搜索")
    print("=" * 60)
    result = manager.search_product("筋膜枪")
    print(json.dumps(result, ensure_ascii=False, indent=2))
