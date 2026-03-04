# -*- coding: utf-8 -*-
"""
Brave Search API 客户端
用于搜索AI领域相关新闻
"""
import os
import sys
import time
import requests
from typing import List, Dict, Optional
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BRAVE_SEARCH_CONFIG, CRAWLER_CONFIG


class BraveSearchClient:
    """Brave Search API 客户端"""
    
    def __init__(self):
        self.api_key = BRAVE_SEARCH_CONFIG["api_key"]
        self.base_url = BRAVE_SEARCH_CONFIG["base_url"]
        self.results_per_query = BRAVE_SEARCH_CONFIG.get("results_per_query", 15)
        self.freshness = BRAVE_SEARCH_CONFIG.get("freshness", "pd")  # 过去24小时
        self.request_interval = CRAWLER_CONFIG.get("request_interval", 1.0)
        self._last_request_time = 0
    
    def _rate_limit(self):
        """请求限速"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self._last_request_time = time.time()
    
    def search(self, query: str, count: int = None) -> List[Dict]:
        """
        执行搜索
        
        Args:
            query: 搜索关键词
            count: 返回结果数量
        
        Returns:
            搜索结果列表
        """
        self._rate_limit()
        
        if count is None:
            count = self.results_per_query
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }
        
        params = {
            "q": query,
            "count": count,
            "freshness": self.freshness,
            "text_decorations": False,
            "search_lang": "zh-hans",
            "country": "cn",
        }
        
        try:
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=CRAWLER_CONFIG.get("timeout", 30)
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            web_results = data.get("web", {}).get("results", [])
            
            for item in web_results:
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("url", ""),
                    "summary": item.get("description", ""),
                    "source": item.get("profile", {}).get("name", "") or self._extract_source(item.get("url", "")),
                    "age": item.get("age", ""),
                    "platform": "brave_search",
                })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ 搜索请求失败 [{query}]: {e}")
            return []
        except Exception as e:
            print(f"   ⚠️ 搜索处理异常 [{query}]: {e}")
            return []
    
    def _extract_source(self, url: str) -> str:
        """从URL提取来源"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            return domain.split(".")[0] if domain else ""
        except:
            return ""


if __name__ == "__main__":
    # 测试
    client = BraveSearchClient()
    results = client.search("ChatGPT 最新", count=5)
    for r in results:
        print(f"- {r['title'][:50]}... ({r['source']})")
