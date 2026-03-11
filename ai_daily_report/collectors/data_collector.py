# -*- coding: utf-8 -*-
"""
AI日报系统 - 数据采集模块
负责从多个来源采集AI领域相关新闻
"""
import os
import sys
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    BRAVE_SEARCH_CONFIG, KEYWORDS, AI_FILTER, 
    KEY_COMPANIES, STORAGE_CONFIG, CRAWLER_CONFIG
)
from utils.brave_search import BraveSearchClient


class AIDataCollector:
    """AI日报数据采集器"""
    
    def __init__(self):
        """初始化采集器"""
        self.brave_client = BraveSearchClient()
        
        # 去重机制
        self._seen_urls = set()
        self._seen_titles = set()
        self._historical_hashes = self._load_historical_hashes()
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要目录存在"""
        for dir_name in ["data", "cache", "reports", "logs"]:
            dir_path = Path(__file__).parent.parent / dir_name
            dir_path.mkdir(exist_ok=True)
    
    def _load_historical_hashes(self) -> set:
        """加载历史数据哈希，用于判断新旧"""
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
        """保存历史哈希"""
        hash_file = Path(__file__).parent.parent / "data" / "historical_hashes.json"
        all_hashes = list(self._historical_hashes.union(set(new_hashes)))
        # 只保留最近7天的哈希（约5000条）
        all_hashes = all_hashes[-5000:]
        
        with open(hash_file, "w", encoding="utf-8") as f:
            json.dump({"hashes": all_hashes, "updated": datetime.now().isoformat()}, f)
    
    def _compute_hash(self, title: str) -> str:
        """计算标题哈希"""
        # 移除空格和标点，统一小写
        normalized = re.sub(r'[^\w]', '', title.lower())
        return hashlib.md5(normalized.encode()).hexdigest()[:16]
    
    def collect_all(self) -> List[Dict]:
        """
        执行全量数据采集 - 核心入口
        返回去重、过滤、排序后的新闻列表
        """
        print("\n" + "="*60)
        print("🤖 AI日报数据采集开始")
        print("="*60)
        
        all_results = []
        
        # 1. 采集核心关键词新闻
        print("\n📡 采集核心AI新闻...")
        primary_news = self._collect_primary_news()
        all_results.extend(primary_news)
        print(f"   ✓ 核心新闻: {len(primary_news)}条")
        
        # 2. 采集大模型厂商动态
        print("\n🏢 采集大模型厂商动态...")
        vendor_news = self._collect_vendor_news()
        all_results.extend(vendor_news)
        print(f"   ✓ 厂商动态: {len(vendor_news)}条")
        
        # 3. 采集AI应用领域新闻
        print("\n🎯 采集AI应用领域新闻...")
        app_news = self._collect_application_news()
        all_results.extend(app_news)
        print(f"   ✓ 应用新闻: {len(app_news)}条")
        
        # 4. 采集技术突破新闻
        print("\n🔬 采集技术突破新闻...")
        tech_news = self._collect_tech_news()
        all_results.extend(tech_news)
        print(f"   ✓ 技术新闻: {len(tech_news)}条")
        
        # 5. 采集行业动态新闻（融资/收购/政策/AGI等）
        print("\n📈 采集行业动态新闻...")
        industry_news = self._collect_industry_news()
        all_results.extend(industry_news)
        print(f"   ✓ 行业动态: {len(industry_news)}条")
        
        # 5. 去重处理
        print("\n🔄 执行去重处理...")
        unique_results = self._deduplicate(all_results)
        print(f"   ✓ 去重后: {len(unique_results)}条 (原{len(all_results)}条)")
        
        # 6. AI相关性过滤
        print("\n🎯 执行相关性过滤...")
        filtered_results = self._filter_ai_related(unique_results)
        print(f"   ✓ 过滤后: {len(filtered_results)}条")
        
        # 7. 计算价值度和排序
        print("\n📊 计算价值度...")
        for item in filtered_results:
            item["value_score"] = self._calculate_value_score(item)
            item["is_new"] = self._is_new_item(item)
        
        # 按价值度排序
        filtered_results.sort(key=lambda x: (x.get("is_new", False), x.get("value_score", 0)), reverse=True)
        
        # 8. 保存原始数据
        self._save_raw_data(filtered_results)
        
        # 9. 更新历史哈希
        new_hashes = [self._compute_hash(item.get("title", "")) for item in filtered_results]
        self._save_historical_hashes(new_hashes)
        
        print(f"\n✅ 采集完成，共{len(filtered_results)}条有效新闻")
        print("="*60 + "\n")
        
        return filtered_results
    
    def _collect_primary_news(self) -> List[Dict]:
        """采集核心关键词新闻"""
        results = []
        for keyword in KEYWORDS["primary"]:
            items = self.brave_client.search(keyword, count=10)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "primary"
            results.extend(items)
        return results
    
    def _collect_vendor_news(self) -> List[Dict]:
        """采集大模型厂商动态"""
        results = []
        for keyword in KEYWORDS["llm_vendors"][:8]:  # 限制数量避免请求过多
            items = self.brave_client.search(keyword, count=5)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "vendor"
            results.extend(items)
        return results
    
    def _collect_application_news(self) -> List[Dict]:
        """采集AI应用领域新闻"""
        results = []
        for keyword in KEYWORDS["applications"][:6]:
            items = self.brave_client.search(keyword, count=5)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "application"
            results.extend(items)
        return results
    
    def _collect_tech_news(self) -> List[Dict]:
        """采集技术突破新闻"""
        results = []
        for keyword in KEYWORDS["technology"]:
            items = self.brave_client.search(keyword, count=5)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "technology"
            results.extend(items)
        return results
    
    def _collect_industry_news(self) -> List[Dict]:
        """采集行业动态新闻（融资/收购/政策/AGI等）"""
        results = []
        for keyword in KEYWORDS["industry"]:
            items = self.brave_client.search(keyword, count=5)
            for item in items:
                item["search_keyword"] = keyword
                item["category"] = "industry"
            results.extend(items)
        return results
    
    def _deduplicate(self, items: List[Dict]) -> List[Dict]:
        """去重处理"""
        unique_items = []
        
        for item in items:
            url = item.get("link", "")
            title = item.get("title", "")
            
            # URL去重
            if url in self._seen_urls:
                continue
            
            # 标题相似度去重
            title_hash = self._compute_hash(title)
            if title_hash in self._seen_titles:
                continue
            
            self._seen_urls.add(url)
            self._seen_titles.add(title_hash)
            unique_items.append(item)
        
        return unique_items
    
    def _filter_ai_related(self, items: List[Dict]) -> List[Dict]:
        """过滤AI相关内容"""
        filtered = []
        
        for item in items:
            title = item.get("title", "").lower()
            summary = item.get("summary", "").lower()
            content = f"{title} {summary}"
            
            # 检查必须排除的词
            if any(word in content for word in AI_FILTER["must_exclude"]):
                continue
            
            # 检查必须包含的词（至少一个）
            has_ai_keyword = any(word.lower() in content for word in AI_FILTER["must_include"])
            if not has_ai_keyword:
                continue
            
            filtered.append(item)
        
        return filtered
    
    def _calculate_value_score(self, item: Dict) -> float:
        """计算新闻价值度（0-100）"""
        score = 50.0  # 基础分
        
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        content = f"{title} {summary}"
        source = item.get("source", "").lower()
        
        # 1. 相关性加分词
        for word in AI_FILTER["relevance_boost"]:
            if word in content:
                score += 5
        
        # 2. 可信来源加分
        for trusted in AI_FILTER["trusted_sources"]:
            if trusted.lower() in source or trusted.lower() in content:
                score += 10
                break
        
        # 3. 重点公司加分
        all_companies = (
            KEY_COMPANIES["international"] + 
            KEY_COMPANIES["domestic"] + 
            KEY_COMPANIES["applications"]
        )
        mentioned_companies = [c for c in all_companies if c.lower() in content]
        score += min(len(mentioned_companies) * 3, 15)
        
        # 4. 核心关键词加分
        for kw in KEYWORDS["primary"]:
            if kw.lower() in content:
                score += 5
        
        # 5. 类别加分
        category = item.get("category", "")
        if category == "primary":
            score += 10
        elif category == "vendor":
            score += 8
        elif category == "technology":
            score += 6
        
        return min(score, 100)
    
    def _is_new_item(self, item: Dict) -> bool:
        """判断是否为新信息"""
        title = item.get("title", "")
        title_hash = self._compute_hash(title)
        return title_hash not in self._historical_hashes
    
    def _save_raw_data(self, items: List[Dict]):
        """保存原始采集数据"""
        today = datetime.now().strftime("%Y%m%d")
        data_file = Path(__file__).parent.parent / "data" / f"ai_news_{today}.json"
        
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump({
                "date": today,
                "count": len(items),
                "items": items,
            }, f, ensure_ascii=False, indent=2)


# 便捷接口
def collect_ai_news() -> List[Dict]:
    """采集AI新闻的便捷接口"""
    collector = AIDataCollector()
    return collector.collect_all()


if __name__ == "__main__":
    # 测试运行
    news = collect_ai_news()
    print(f"\n采集到 {len(news)} 条AI新闻")
    for i, item in enumerate(news[:5], 1):
        print(f"{i}. [{item.get('value_score', 0):.0f}分] {item.get('title', '')[:50]}")
