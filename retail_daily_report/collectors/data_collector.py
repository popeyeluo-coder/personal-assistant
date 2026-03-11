# -*- coding: utf-8 -*-
"""
零售日报系统 - 数据采集模块
负责从多个来源采集零售行业相关新闻
"""
import os
import sys
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    BRAVE_SEARCH_CONFIG, KEYWORDS, RETAIL_FILTER, 
    KEY_COMPANIES, STORAGE_CONFIG, CRAWLER_CONFIG
)
from utils.brave_search import BraveSearchClient


class RetailDataCollector:
    """零售日报数据采集器"""
    
    def __init__(self):
        self.brave_client = BraveSearchClient()
        self._seen_urls = set()
        self._seen_titles = set()
        self._historical_hashes = self._load_historical_hashes()
        self._ensure_directories()
    
    def _ensure_directories(self):
        for dir_name in ["data", "cache", "reports", "logs"]:
            dir_path = Path(__file__).parent.parent / dir_name
            dir_path.mkdir(exist_ok=True)
    
    def _load_historical_hashes(self) -> set:
        hash_file = Path(__file__).parent.parent / "data" / "historical_hashes.json"
        if hash_file.exists():
            try:
                with open(hash_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return set(data.get("hashes", []))
            except:
                pass
        return set()
    
    def _save_historical_hashes(self, new_hashes: List[str]):
        hash_file = Path(__file__).parent.parent / "data" / "historical_hashes.json"
        all_hashes = list(self._historical_hashes.union(set(new_hashes)))
        all_hashes = all_hashes[-5000:]
        with open(hash_file, "w", encoding="utf-8") as f:
            json.dump({"hashes": all_hashes, "updated": datetime.now().isoformat()}, f)
    
    def _compute_hash(self, title: str) -> str:
        normalized = re.sub(r'[^\w]', '', title.lower())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def collect_all(self) -> List[Dict]:
        """执行全量数据采集"""
        print("\n" + "="*60)
        print("🛒 零售日报数据采集开始")
        print("="*60)
        
        all_results = []
        
        # 1. 核心关键词
        print("\n📡 采集核心零售新闻...")
        primary_news = self._collect_primary_news()
        all_results.extend(primary_news)
        print(f"   ✓ 核心新闻: {len(primary_news)}条")
        
        # 2. 零售业态
        print("\n🏪 采集零售业态动态...")
        format_news = self._collect_format_news()
        all_results.extend(format_news)
        print(f"   ✓ 业态动态: {len(format_news)}条")
        
        # 3. 零售巨头
        print("\n🏢 采集零售巨头动态...")
        giant_news = self._collect_giant_news()
        all_results.extend(giant_news)
        print(f"   ✓ 巨头动态: {len(giant_news)}条")
        
        # 4. 消费趋势
        print("\n👥 采集消费趋势...")
        trend_news = self._collect_trend_news()
        all_results.extend(trend_news)
        print(f"   ✓ 消费趋势: {len(trend_news)}条")
        
        # 5. 零售科技（无人零售/智慧零售/数字化/AI等）
        print("\n🔧 采集零售科技动态...")
        tech_news = self._collect_retail_tech_news()
        all_results.extend(tech_news)
        print(f"   ✓ 零售科技: {len(tech_news)}条")
        
        # 6. 支付与营销
        print("\n💳 采集支付与营销动态...")
        payment_news = self._collect_payment_marketing_news()
        all_results.extend(payment_news)
        print(f"   ✓ 支付营销: {len(payment_news)}条")
        
        # 去重
        print("\n🔄 执行去重处理...")
        unique_results = self._deduplicate(all_results)
        print(f"   ✓ 去重后: {len(unique_results)}条")
        
        # 过滤
        print("\n🎯 执行相关性过滤...")
        filtered_results = self._filter_retail_related(unique_results)
        print(f"   ✓ 过滤后: {len(filtered_results)}条")
        
        # 计算价值度
        print("\n📊 计算价值度...")
        for item in filtered_results:
            item["value_score"] = self._calculate_value_score(item)
            item["is_new"] = self._is_new_item(item)
        
        filtered_results.sort(key=lambda x: (x.get("is_new", False), x.get("value_score", 0)), reverse=True)
        
        self._save_raw_data(filtered_results)
        
        new_hashes = [self._compute_hash(item.get("title", "")) for item in filtered_results]
        self._save_historical_hashes(new_hashes)
        
        print(f"\n✅ 采集完成，共{len(filtered_results)}条有效新闻")
        print("="*60 + "\n")
        
        return filtered_results
    
    def _collect_primary_news(self) -> List[Dict]:
        results = []
        for keyword in KEYWORDS["primary"]:
            items = self.brave_client.search(keyword, count=10)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "primary"
            results.extend(items)
        return results
    
    def _collect_format_news(self) -> List[Dict]:
        results = []
        for keyword in KEYWORDS["retail_formats"]:
            items = self.brave_client.search(keyword, count=5)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "format"
            results.extend(items)
        return results
    
    def _collect_giant_news(self) -> List[Dict]:
        results = []
        for keyword in KEYWORDS["retail_giants"][:6]:
            items = self.brave_client.search(keyword, count=5)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "giant"
            results.extend(items)
        return results
    
    def _collect_trend_news(self) -> List[Dict]:
        results = []
        for keyword in KEYWORDS["consumer_trends"][:4]:
            items = self.brave_client.search(keyword, count=5)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "trend"
            results.extend(items)
        return results
    
    def _collect_retail_tech_news(self) -> List[Dict]:
        """采集零售科技动态（无人零售/智慧零售/数字化/AI等）"""
        results = []
        for keyword in KEYWORDS["retail_tech"]:
            items = self.brave_client.search(keyword, count=5)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "tech"
            results.extend(items)
        return results
    
    def _collect_payment_marketing_news(self) -> List[Dict]:
        """采集支付与营销动态"""
        results = []
        for keyword in KEYWORDS["payment_marketing"]:
            items = self.brave_client.search(keyword, count=5)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "payment"
            results.extend(items)
        return results
    
    def _deduplicate(self, items: List[Dict]) -> List[Dict]:
        unique_items = []
        for item in items:
            url = item.get("link", "")
            title = item.get("title", "")
            if url in self._seen_urls:
                continue
            title_hash = self._compute_hash(title)
            if title_hash in self._seen_titles:
                continue
            self._seen_urls.add(url)
            self._seen_titles.add(title_hash)
            unique_items.append(item)
        return unique_items
    
    def _filter_retail_related(self, items: List[Dict]) -> List[Dict]:
        filtered = []
        for item in items:
            title = item.get("title", "").lower()
            summary = item.get("summary", "").lower()
            content = f"{title} {summary}"
            
            if any(word in content for word in RETAIL_FILTER["must_exclude"]):
                continue
            
            has_keyword = any(word.lower() in content for word in RETAIL_FILTER["must_include"])
            if not has_keyword:
                continue
            
            filtered.append(item)
        return filtered
    
    def _calculate_value_score(self, item: Dict) -> float:
        score = 50.0
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        content = f"{title} {summary}"
        source = item.get("source", "").lower()
        
        for word in RETAIL_FILTER["relevance_boost"]:
            if word in content:
                score += 5
        
        for trusted in RETAIL_FILTER["trusted_sources"]:
            if trusted.lower() in source or trusted.lower() in content:
                score += 10
                break
        
        all_companies = (
            KEY_COMPANIES["convenience"] + KEY_COMPANIES["supermarket"] +
            KEY_COMPANIES["membership"] + KEY_COMPANIES["discount"] +
            KEY_COMPANIES["ecommerce"]
        )
        mentioned = [c for c in all_companies if c.lower() in content]
        score += min(len(mentioned) * 3, 15)
        
        category = item.get("category", "")
        if category == "primary":
            score += 10
        elif category == "format":
            score += 8
        
        return min(score, 100)
    
    def _is_new_item(self, item: Dict) -> bool:
        title = item.get("title", "")
        title_hash = self._compute_hash(title)
        return title_hash not in self._historical_hashes
    
    def _save_raw_data(self, items: List[Dict]):
        today = datetime.now().strftime("%Y%m%d")
        data_file = Path(__file__).parent.parent / "data" / f"retail_news_{today}.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump({"date": today, "count": len(items), "items": items}, f, ensure_ascii=False, indent=2)


def collect_retail_news() -> List[Dict]:
    collector = RetailDataCollector()
    return collector.collect_all()


if __name__ == "__main__":
    news = collect_retail_news()
    print(f"\n采集到 {len(news)} 条零售新闻")
