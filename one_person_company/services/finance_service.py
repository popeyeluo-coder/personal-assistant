"""
金融数据服务 - A股/港股/美股数据获取
使用免费数据源：AKShare、yfinance、东方财富
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)


class FinanceService:
    """
    金融数据服务
    支持：A股、港股、美股实时和历史数据
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self._akshare_available = self._check_akshare()
        self._yfinance_available = self._check_yfinance()
        
    def _check_akshare(self) -> bool:
        """检查AKShare是否可用"""
        try:
            import akshare
            return True
        except ImportError:
            logger.warning("AKShare未安装，部分A股功能不可用")
            return False
    
    def _check_yfinance(self) -> bool:
        """检查yfinance是否可用"""
        try:
            import yfinance
            return True
        except ImportError:
            logger.warning("yfinance未安装，美股功能不可用")
            return False
    
    # ==================== A股数据 ====================
    
    def get_a_stock_realtime(self, stock_code: str) -> Dict:
        """
        获取A股实时行情
        
        Args:
            stock_code: 股票代码，如 "600519" 或 "000001"
        """
        if self._akshare_available:
            return self._get_a_stock_akshare(stock_code)
        else:
            return self._get_a_stock_eastmoney(stock_code)
    
    def _get_a_stock_akshare(self, stock_code: str) -> Dict:
        """使用AKShare获取A股数据"""
        try:
            import akshare as ak
            
            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == stock_code]
            
            if stock_data.empty:
                return {"status": "error", "message": f"未找到股票 {stock_code}"}
            
            row = stock_data.iloc[0]
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "market": "A股",
                "data": {
                    "code": stock_code,
                    "name": row.get("名称", ""),
                    "price": float(row.get("最新价", 0)),
                    "change": float(row.get("涨跌额", 0)),
                    "change_pct": float(row.get("涨跌幅", 0)),
                    "volume": float(row.get("成交量", 0)),
                    "amount": float(row.get("成交额", 0)),
                    "high": float(row.get("最高", 0)),
                    "low": float(row.get("最低", 0)),
                    "open": float(row.get("今开", 0)),
                    "prev_close": float(row.get("昨收", 0))
                }
            }
        except Exception as e:
            logger.error(f"AKShare获取A股数据失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_a_stock_eastmoney(self, stock_code: str) -> Dict:
        """使用东方财富API获取A股数据（免费）"""
        try:
            # 判断市场
            market = "1" if stock_code.startswith("6") else "0"
            
            url = f"https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": f"{market}.{stock_code}",
                "fields": "f43,f44,f45,f46,f47,f48,f57,f58,f60,f170,f171"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get("data"):
                d = data["data"]
                return {
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "market": "A股",
                    "data": {
                        "code": stock_code,
                        "name": d.get("f58", ""),
                        "price": d.get("f43", 0) / 100,
                        "change_pct": d.get("f170", 0) / 100,
                        "high": d.get("f44", 0) / 100,
                        "low": d.get("f45", 0) / 100,
                        "open": d.get("f46", 0) / 100,
                        "volume": d.get("f47", 0),
                        "amount": d.get("f48", 0)
                    }
                }
            else:
                return {"status": "error", "message": "数据获取失败"}
                
        except Exception as e:
            logger.error(f"东方财富API获取数据失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_a_stock_history(self, stock_code: str, days: int = 30) -> Dict:
        """获取A股历史数据"""
        if not self._akshare_available:
            return {"status": "error", "message": "需要安装akshare: pip install akshare"}
        
        try:
            import akshare as ak
            
            # 判断市场前缀
            symbol = f"sh{stock_code}" if stock_code.startswith("6") else f"sz{stock_code}"
            
            df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                                    start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d"),
                                    end_date=datetime.now().strftime("%Y%m%d"))
            
            history = []
            for _, row in df.iterrows():
                history.append({
                    "date": str(row.get("日期", "")),
                    "open": float(row.get("开盘", 0)),
                    "close": float(row.get("收盘", 0)),
                    "high": float(row.get("最高", 0)),
                    "low": float(row.get("最低", 0)),
                    "volume": float(row.get("成交量", 0)),
                    "amount": float(row.get("成交额", 0)),
                    "change_pct": float(row.get("涨跌幅", 0))
                })
            
            return {
                "status": "success",
                "code": stock_code,
                "days": days,
                "history": history
            }
            
        except Exception as e:
            logger.error(f"获取历史数据失败: {e}")
            return {"status": "error", "message": str(e)}
    
    # ==================== 港股数据 ====================
    
    def get_hk_stock_realtime(self, stock_code: str) -> Dict:
        """
        获取港股实时行情
        
        Args:
            stock_code: 港股代码，如 "00700" (腾讯)
        """
        if self._akshare_available:
            return self._get_hk_stock_akshare(stock_code)
        else:
            return self._get_hk_stock_sina(stock_code)
    
    def _get_hk_stock_akshare(self, stock_code: str) -> Dict:
        """使用AKShare获取港股数据"""
        try:
            import akshare as ak
            
            df = ak.stock_hk_spot_em()
            stock_data = df[df['代码'] == stock_code]
            
            if stock_data.empty:
                return {"status": "error", "message": f"未找到港股 {stock_code}"}
            
            row = stock_data.iloc[0]
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "market": "港股",
                "data": {
                    "code": stock_code,
                    "name": row.get("名称", ""),
                    "price": float(row.get("最新价", 0)),
                    "change_pct": float(row.get("涨跌幅", 0)),
                    "volume": float(row.get("成交量", 0)),
                    "amount": float(row.get("成交额", 0))
                }
            }
        except Exception as e:
            logger.error(f"AKShare获取港股数据失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_hk_stock_sina(self, stock_code: str) -> Dict:
        """使用新浪API获取港股数据"""
        try:
            url = f"https://hq.sinajs.cn/list=hk{stock_code}"
            headers = {"Referer": "https://finance.sina.com.cn"}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'gbk'
            
            content = response.text
            # 解析新浪数据格式
            match = content.split('="')[1].rstrip('";').split(',') if '="' in content else []
            
            if len(match) >= 10:
                return {
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "market": "港股",
                    "data": {
                        "code": stock_code,
                        "name": match[1],
                        "price": float(match[6]),
                        "change": float(match[7]),
                        "change_pct": float(match[8]),
                        "prev_close": float(match[3]),
                        "open": float(match[2]),
                        "high": float(match[4]),
                        "low": float(match[5])
                    }
                }
            else:
                return {"status": "error", "message": "数据解析失败"}
                
        except Exception as e:
            logger.error(f"新浪API获取港股数据失败: {e}")
            return {"status": "error", "message": str(e)}
    
    # ==================== 美股数据 ====================
    
    def get_us_stock_realtime(self, symbol: str) -> Dict:
        """
        获取美股实时行情
        
        Args:
            symbol: 股票代码，如 "AAPL", "TSLA"
        """
        if self._yfinance_available:
            return self._get_us_stock_yfinance(symbol)
        else:
            return {"status": "error", "message": "需要安装yfinance: pip install yfinance"}
    
    def _get_us_stock_yfinance(self, symbol: str) -> Dict:
        """使用yfinance获取美股数据"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "market": "美股",
                "data": {
                    "symbol": symbol,
                    "name": info.get("longName", ""),
                    "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
                    "change": info.get("regularMarketChange", 0),
                    "change_pct": info.get("regularMarketChangePercent", 0),
                    "volume": info.get("regularMarketVolume", 0),
                    "market_cap": info.get("marketCap", 0),
                    "pe_ratio": info.get("trailingPE", 0),
                    "52w_high": info.get("fiftyTwoWeekHigh", 0),
                    "52w_low": info.get("fiftyTwoWeekLow", 0)
                }
            }
        except Exception as e:
            logger.error(f"yfinance获取美股数据失败: {e}")
            return {"status": "error", "message": str(e)}
    
    # ==================== 市场概览 ====================
    
    def get_market_overview(self) -> Dict:
        """获取市场概览"""
        overview = {
            "timestamp": datetime.now().isoformat(),
            "markets": {}
        }
        
        # A股指数
        if self._akshare_available:
            try:
                import akshare as ak
                df = ak.stock_zh_index_spot()
                
                indices = {"上证指数": "000001", "深证成指": "399001", "创业板指": "399006"}
                for name, code in indices.items():
                    idx_data = df[df['代码'] == code]
                    if not idx_data.empty:
                        row = idx_data.iloc[0]
                        overview["markets"][name] = {
                            "price": float(row.get("最新价", 0)),
                            "change_pct": float(row.get("涨跌幅", 0))
                        }
            except Exception as e:
                logger.error(f"获取A股指数失败: {e}")
        
        return overview
    
    def get_stock_news(self, stock_code: str) -> Dict:
        """获取股票相关新闻"""
        from .search_service import SearchService
        search = SearchService()
        
        result = search.search_news(f"股票 {stock_code}", count=5)
        return result
    
    # ==================== 你跟踪的股票 ====================
    
    def get_watchlist_status(self) -> Dict:
        """
        获取关注股票状态
        基于你的配置：宏达股份、雅化集团等
        """
        watchlist = [
            {"code": "600331", "name": "宏达股份", "market": "A"},
            {"code": "002497", "name": "雅化集团", "market": "A"},
            {"code": "601777", "name": "力帆科技", "market": "A"},
            {"code": "00354", "name": "中国软件国际", "market": "HK"},
            {"code": "00700", "name": "腾讯控股", "market": "HK"}
        ]
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "stocks": []
        }
        
        for stock in watchlist:
            if stock["market"] == "A":
                data = self.get_a_stock_realtime(stock["code"])
            else:
                data = self.get_hk_stock_realtime(stock["code"])
            
            if data.get("status") == "success":
                status["stocks"].append({
                    **stock,
                    **data.get("data", {})
                })
            else:
                status["stocks"].append({
                    **stock,
                    "error": data.get("message", "获取失败")
                })
        
        return status


# 测试
if __name__ == "__main__":
    service = FinanceService()
    
    # 测试A股
    print("=" * 50)
    print("测试A股数据 - 贵州茅台")
    result = service.get_a_stock_realtime("600519")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试关注列表
    print("\n" + "=" * 50)
    print("测试关注股票")
    result = service.get_watchlist_status()
    print(json.dumps(result, ensure_ascii=False, indent=2))
