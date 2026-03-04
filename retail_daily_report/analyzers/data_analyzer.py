# -*- coding: utf-8 -*-
"""
零售日报系统 - 数据分析模块
"""
import sys
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DIMENSION_SYSTEM, KEY_COMPANIES, KEYWORDS


class RetailDataAnalyzer:
    """零售日报数据分析器"""
    
    def __init__(self):
        self._init_dimension_system()
        self._init_importance_rules()
    
    def _init_dimension_system(self):
        self.dimensions = DIMENSION_SYSTEM
    
    def _init_importance_rules(self):
        self.high_importance_keywords = [
            "开业", "关店", "首店", "旗舰店", "融资", "收购",
            "扩张", "撤出", "战略", "独家", "重磅",
        ]
        self.medium_importance_keywords = [
            "合作", "新品", "升级", "促销", "会员", "数字化",
        ]
        self.key_companies = (
            KEY_COMPANIES["convenience"] + KEY_COMPANIES["supermarket"] +
            KEY_COMPANIES["membership"] + KEY_COMPANIES["discount"]
        )
    
    def analyze_all(self, collected_data: List[Dict]) -> Dict[str, Any]:
        print("\n📊 开始数据分析...")
        analyzed_items = []
        
        for item in collected_data:
            dimension = self._classify_dimension(item)
            item["dimension"] = dimension
            
            importance = self._evaluate_importance(item)
            item["importance"] = importance
            
            companies = self._extract_companies(item)
            item["companies"] = companies
            
            brief_comment = self._generate_brief_comment(item)
            item["brief_comment"] = brief_comment
            
            priority = self._calculate_priority(item)
            item["priority"] = priority
            
            analyzed_items.append(item)
        
        summary = self._generate_executive_summary(analyzed_items)
        expert_overview = self._generate_expert_overview(analyzed_items)
        
        print(f"   ✓ 分析完成，共{len(analyzed_items)}条")
        
        return {
            "items": analyzed_items,
            "summary": summary,
            "expert_overview": expert_overview,
            "total_items": len(analyzed_items),
        }
    
    def _classify_dimension(self, item: Dict) -> Dict:
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        content = f"{title} {summary}"
        
        best_dimension = None
        best_score = 0
        
        for dim_key, dim_info in self.dimensions.items():
            score = sum(1 for kw in dim_info["keywords"] if kw.lower() in content)
            if score > best_score:
                best_score = score
                best_dimension = {
                    "key": dim_key,
                    "name": dim_info["name"],
                    "icon": dim_info["icon"],
                    "priority_boost": dim_info["priority_boost"],
                }
        
        if best_dimension is None:
            best_dimension = {"key": "other", "name": "行业动态", "icon": "📰", "priority_boost": 0}
        
        return best_dimension
    
    def _evaluate_importance(self, item: Dict) -> Dict:
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        content = f"{title} {summary}"
        
        high_count = sum(1 for kw in self.high_importance_keywords if kw.lower() in content)
        medium_count = sum(1 for kw in self.medium_importance_keywords if kw.lower() in content)
        company_mentions = sum(1 for c in self.key_companies if c.lower() in content)
        
        score = high_count * 10 + medium_count * 5 + company_mentions * 3
        
        if score >= 25:
            return {"level": "high", "level_cn": "高", "score": score, "color": "#dc3545"}
        elif score >= 12:
            return {"level": "medium", "level_cn": "中", "score": score, "color": "#fd7e14"}
        else:
            return {"level": "low", "level_cn": "低", "score": score, "color": "#28a745"}
    
    def _extract_companies(self, item: Dict) -> List[str]:
        title = item.get("title", "")
        summary = item.get("summary", "")
        content = f"{title} {summary}"
        
        all_companies = (
            KEY_COMPANIES["convenience"] + KEY_COMPANIES["supermarket"] +
            KEY_COMPANIES["membership"] + KEY_COMPANIES["discount"] +
            KEY_COMPANIES["ecommerce"]
        )
        return [c for c in all_companies if c in content][:5]
    
    def _generate_brief_comment(self, item: Dict) -> str:
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        content = f"{title} {summary}"
        
        dimension = item.get("dimension", {})
        importance = item.get("importance", {})
        companies = item.get("companies", [])
        is_new = item.get("is_new", False)
        
        dim_name = dimension.get("name", "其他")
        imp_level = importance.get("level", "low")
        
        if dim_name == "开店扩张":
            if imp_level == "high":
                comment = f"🏪 高价值 | 重要开店动态，行业扩张信号"
            else:
                comment = "🏪 开店动态 | 零售网点扩张"
        elif dim_name == "闭店收缩":
            if imp_level == "high":
                comment = f"⚠️ 重点关注 | 重要闭店信号，行业调整"
            else:
                comment = "🚫 闭店动态 | 市场调整信号"
        elif dim_name == "融资并购":
            comment = "💰 资本动态 | 行业投融资，关注估值变化"
        elif dim_name == "业态创新":
            comment = "💡 创新动态 | 新模式新业态，值得关注"
        elif dim_name == "科技赋能":
            comment = "🔧 科技赋能 | 数字化转型动态"
        elif dim_name == "促销活动":
            comment = "🎁 促销活动 | 营销动态参考"
        elif dim_name == "供应链":
            comment = "📦 供应链 | 后端能力建设"
        elif dim_name == "消费洞察":
            comment = "👥 消费洞察 | 消费趋势参考"
        elif dim_name == "行业报告":
            comment = "📊 行业报告 | 数据参考价值"
        else:
            comment = "📰 行业动态 | 一般性资讯"
        
        if is_new:
            comment = f"[新] {comment}"
        
        return comment
    
    def _calculate_priority(self, item: Dict) -> str:
        value_score = item.get("value_score", 50)
        importance = item.get("importance", {})
        dimension = item.get("dimension", {})
        is_new = item.get("is_new", False)
        
        total_score = (
            value_score * 0.4 + 
            importance.get("score", 0) * 0.3 + 
            dimension.get("priority_boost", 0) + 
            (20 if is_new else 0)
        )
        
        if total_score >= 60:
            return "P1"
        elif total_score >= 40:
            return "P2"
        elif total_score >= 25:
            return "P3"
        else:
            return "P4"
    
    def _generate_executive_summary(self, items: List[Dict]) -> Dict:
        dimension_counts = Counter(item.get("dimension", {}).get("name", "其他") for item in items)
        priority_counts = Counter(item.get("priority", "P4") for item in items)
        
        all_companies = []
        for item in items:
            all_companies.extend(item.get("companies", []))
        hot_companies = [c for c, _ in Counter(all_companies).most_common(10)]
        
        new_count = sum(1 for item in items if item.get("is_new", False))
        
        return {
            "dimension_counts": dict(dimension_counts),
            "priority_counts": dict(priority_counts),
            "hot_companies": hot_companies,
            "new_count": new_count,
            "old_count": len(items) - new_count,
        }
    
    def _generate_expert_overview(self, items: List[Dict]) -> Dict:
        total = len(items)
        if total == 0:
            return {
                "overview": "今日暂无重要零售动态。",
                "key_trends": [],
                "recommendations": [],
                "risk_level": "低",
                "risk_color": "#28a745",
            }
        
        p1_count = sum(1 for item in items if item.get("priority") == "P1")
        p2_count = sum(1 for item in items if item.get("priority") == "P2")
        new_count = sum(1 for item in items if item.get("is_new", False))
        
        dim_counter = Counter(item.get("dimension", {}).get("name", "") for item in items)
        top_dimensions = [d for d, _ in dim_counter.most_common(3)]
        
        all_companies = []
        for item in items:
            all_companies.extend(item.get("companies", []))
        top_companies = [c for c, _ in Counter(all_companies).most_common(5)]
        
        overview_parts = []
        
        if p1_count >= 3:
            overview_parts.append(f"🔥 今日零售行业动态活跃：发现{p1_count}条高优信息。")
            risk_level = "高"
            risk_color = "#dc3545"
        elif p1_count >= 1:
            overview_parts.append(f"📈 今日发现{p1_count}条高优、{p2_count}条重要信息。")
            risk_level = "中"
            risk_color = "#fd7e14"
        else:
            overview_parts.append(f"📊 今日共{total}条零售资讯，整体平稳。")
            risk_level = "低"
            risk_color = "#28a745"
        
        if top_dimensions:
            overview_parts.append(f"热点方向：{', '.join(top_dimensions)}。")
        
        if top_companies:
            overview_parts.append(f"重点关注：{', '.join(top_companies[:3])}。")
        
        key_trends = []
        if "开店扩张" in top_dimensions:
            key_trends.append("🏪 开店活跃：零售扩张势头明显")
        if "闭店收缩" in top_dimensions:
            key_trends.append("⚠️ 闭店信号：部分业态面临调整")
        if "融资并购" in top_dimensions:
            key_trends.append("💰 资本活跃：投融资动态频繁")
        if "业态创新" in top_dimensions:
            key_trends.append("💡 创新加速：新业态新模式涌现")
        
        if not key_trends:
            key_trends.append("📊 今日无显著趋势，市场相对平稳")
        
        recommendations = []
        if p1_count > 0:
            recommendations.append(f"⚡ 优先阅读{p1_count}条高优新闻")
        if top_companies:
            recommendations.append(f"🎯 关注{top_companies[0]}最新动态")
        if "闭店收缩" in top_dimensions:
            recommendations.append("⚠️ 留意闭店信号，评估市场变化")
        
        if not recommendations:
            recommendations.append("✅ 今日态势平稳，保持常规关注")
        
        return {
            "overview": " ".join(overview_parts),
            "key_trends": key_trends[:4],
            "recommendations": recommendations[:4],
            "risk_level": risk_level,
            "risk_color": risk_color,
        }


def analyze_retail_news(collected_data: List[Dict]) -> Dict:
    return RetailDataAnalyzer().analyze_all(collected_data)
