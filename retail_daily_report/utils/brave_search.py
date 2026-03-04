# -*- coding: utf-8 -*-
"""
Brave Search API 客户端
"""
import os
import sys
import time
import requests
from typing import List, Dict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import BRAVE_SEARCH_CONFIG, CRAWLER_CONFIG


class BraveSearchClient:
    def __init__(self):
        self.api_key = BRAVE_SEARCH_CONFIG["api_key"]
        self.base_url = BRAVE_SEARCH_CONFIG["base_url"]
        self.results_per_query = BRAVE_SEARCH_CONFIG.get("results_per_query", 15)
        self.freshness = BRAVE_SEARCH_CONFIG.get("freshness", "pd")
        self.request_interval = CRAWLER_CONFIG.get("request_interval", 1.0)
        self._last_request_time = 0
    
    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self.request_interval:
            time.sleep(self.request_interval - elapsed)
        self._last_request_time = time.time()
    
    def search(self, query: str, count: int = None) -> List[Dict]:
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
            response = requests.get(self.base_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("web", {}).get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("url", ""),
                    "summary": item.get("description", ""),
                    "source": item.get("profile", {}).get("name", ""),
                    "age": item.get("age", ""),
                    "platform": "brave_search",
                })
            return results
        except Exception as e:
            print(f"   ⚠️ 搜索失败 [{query}]: {e}")
            return []
