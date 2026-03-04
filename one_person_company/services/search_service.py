"""
搜索服务 - 使用 Brave Search API 进行市场调研
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class SearchService:
    """
    搜索服务 - 支持多种搜索引擎
    主要用于：市场调研、趋势分析、竞品研究
    """
    
    def __init__(self, api_key: str = None):
        self.brave_api_key = api_key or os.getenv('BRAVE_API_KEY', 'BSA2f0EsW7yU8canxgUOnfwYvhlUY1L')
        self.brave_base_url = "https://api.search.brave.com/res/v1"
        self.cache = {}
        
    def search_web(self, query: str, count: int = 10, freshness: str = None) -> Dict:
        """
        网页搜索
        
        Args:
            query: 搜索关键词
            count: 返回结果数量
            freshness: 时间过滤 (pd=过去24小时, pw=过去一周, pm=过去一月)
        """
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key
            }
            
            params = {
                "q": query,
                "count": count
            }
            
            if freshness:
                params["freshness"] = freshness
            
            response = requests.get(
                f"{self.brave_base_url}/web/search",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "results": self._parse_web_results(data)
                }
            else:
                logger.error(f"搜索失败: {response.status_code} - {response.text}")
                return {"status": "error", "message": response.text}
                
        except Exception as e:
            logger.error(f"搜索异常: {e}")
            return {"status": "error", "message": str(e)}
    
    def _parse_web_results(self, data: Dict) -> List[Dict]:
        """解析网页搜索结果"""
        results = []
        
        web_results = data.get("web", {}).get("results", [])
        for item in web_results:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "age": item.get("age", ""),
                "source": item.get("profile", {}).get("name", "")
            })
        
        return results
    
    def search_news(self, query: str, count: int = 10) -> Dict:
        """
        新闻搜索 - 用于追踪行业动态
        """
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key
            }
            
            params = {
                "q": query,
                "count": count
            }
            
            response = requests.get(
                f"{self.brave_base_url}/news/search",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "news": self._parse_news_results(data)
                }
            else:
                return {"status": "error", "message": response.text}
                
        except Exception as e:
            logger.error(f"新闻搜索异常: {e}")
            return {"status": "error", "message": str(e)}
    
    def _parse_news_results(self, data: Dict) -> List[Dict]:
        """解析新闻搜索结果"""
        results = []
        
        news_results = data.get("results", [])
        for item in news_results:
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
                "source": item.get("meta_url", {}).get("hostname", ""),
                "age": item.get("age", ""),
                "thumbnail": item.get("thumbnail", {}).get("src", "")
            })
        
        return results
    
    def search_trends(self, keywords: List[str]) -> Dict:
        """
        趋势搜索 - 分析多个关键词的热度
        """
        trends = {}
        
        for keyword in keywords:
            result = self.search_web(keyword, count=5, freshness="pm")
            if result.get("status") == "success":
                trends[keyword] = {
                    "results_count": len(result.get("results", [])),
                    "top_results": result.get("results", [])[:3],
                    "search_time": result.get("timestamp")
                }
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "trends": trends
        }
    
    def search_products(self, product_name: str, platform: str = None) -> Dict:
        """
        产品搜索 - 用于选品分析
        
        Args:
            product_name: 产品名称
            platform: 指定平台 (抖音/淘宝/1688等)
        """
        queries = []
        
        if platform:
            queries.append(f"{product_name} {platform}")
        else:
            # 多平台搜索
            queries = [
                f"{product_name} 抖音爆款",
                f"{product_name} 1688货源",
                f"{product_name} 销量排行"
            ]
        
        all_results = {}
        for query in queries:
            result = self.search_web(query, count=5)
            if result.get("status") == "success":
                all_results[query] = result.get("results", [])
        
        return {
            "status": "success",
            "product": product_name,
            "timestamp": datetime.now().isoformat(),
            "search_results": all_results
        }
    
    def search_competitors(self, business_type: str, keywords: List[str]) -> Dict:
        """
        竞品搜索 - 分析竞争对手
        """
        competitors = []
        
        for keyword in keywords:
            query = f"{business_type} {keyword} 竞品分析"
            result = self.search_web(query, count=5)
            if result.get("status") == "success":
                competitors.extend(result.get("results", []))
        
        return {
            "status": "success",
            "business_type": business_type,
            "timestamp": datetime.now().isoformat(),
            "competitors": competitors[:10]  # 去重后取前10
        }
    
    def search_market_insights(self, industry: str) -> Dict:
        """
        市场洞察 - 获取行业报告和分析
        """
        queries = [
            f"{industry} 行业报告 2024",
            f"{industry} 市场规模 增长率",
            f"{industry} 发展趋势",
            f"{industry} 头部玩家 市场份额"
        ]
        
        insights = {}
        for query in queries:
            result = self.search_web(query, count=3)
            if result.get("status") == "success":
                insights[query] = result.get("results", [])
        
        return {
            "status": "success",
            "industry": industry,
            "timestamp": datetime.now().isoformat(),
            "insights": insights
        }


# 测试代码
if __name__ == "__main__":
    service = SearchService()
    
    # 测试网页搜索
    print("=" * 50)
    print("测试网页搜索")
    result = service.search_web("抖音电商 爆款产品", count=3)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试产品搜索
    print("\n" + "=" * 50)
    print("测试产品搜索")
    result = service.search_products("筋膜枪")
    print(json.dumps(result, ensure_ascii=False, indent=2))
