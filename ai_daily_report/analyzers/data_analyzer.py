# -*- coding: utf-8 -*-
"""
AI日报系统 - 数据分析模块
负责对采集的AI新闻进行分类、评估和洞察
"""
import sys
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from collections import Counter

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import DIMENSION_SYSTEM, KEY_COMPANIES, KEYWORDS


class AIDataAnalyzer:
    """AI日报数据分析器"""
    
    def __init__(self):
        """初始化分析器"""
        self._init_dimension_system()
        self._init_importance_rules()
    
    def _init_dimension_system(self):
        """初始化维度体系"""
        self.dimensions = DIMENSION_SYSTEM
    
    def _init_importance_rules(self):
        """初始化重要性评估规则"""
        # 高重要性关键词
        self.high_importance_keywords = [
            "突破", "首次", "重磅", "独家", "发布", "开源",
            "融资", "收购", "上线", "官宣", "GPT-5", "AGI",
            "超越", "领先", "创纪录", "里程碑",
        ]
        
        # 中重要性关键词
        self.medium_importance_keywords = [
            "合作", "更新", "升级", "优化", "功能", "测试",
            "beta", "preview", "应用", "部署", "案例",
        ]
        
        # 重点公司
        self.key_companies = (
            KEY_COMPANIES["international"] + 
            KEY_COMPANIES["domestic"]
        )
    
    def analyze_all(self, collected_data: List[Dict]) -> Dict[str, Any]:
        """
        执行全面分析 - 核心入口
        
        Args:
            collected_data: 采集的原始数据
        
        Returns:
            分析结果字典
        """
        print("\n📊 开始数据分析...")
        
        analyzed_items = []
        
        for item in collected_data:
            # 1. 维度分类
            dimension = self._classify_dimension(item)
            item["dimension"] = dimension
            
            # 2. 重要性评估
            importance = self._evaluate_importance(item)
            item["importance"] = importance
            
            # 3. 提取关联公司
            companies = self._extract_companies(item)
            item["companies"] = companies
            
            # 4. 生成专家小评
            brief_comment = self._generate_brief_comment(item)
            item["brief_comment"] = brief_comment
            
            # 5. 计算综合优先级
            priority = self._calculate_priority(item)
            item["priority"] = priority
            
            analyzed_items.append(item)
        
        # 生成执行摘要
        summary = self._generate_executive_summary(analyzed_items)
        
        # 生成专家总评
        expert_overview = self._generate_expert_overview(analyzed_items)
        
        print(f"   ✓ 分析完成，共{len(analyzed_items)}条")
        
        return {
            "items": analyzed_items,
            "summary": summary,
            "expert_overview": expert_overview,
            "total_items": len(analyzed_items),
        }
    
    def _classify_dimension(self, item: Dict) -> Dict:
        """对新闻进行维度分类"""
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        content = f"{title} {summary}"
        
        best_dimension = None
        best_score = 0
        
        for dim_key, dim_info in self.dimensions.items():
            score = 0
            for keyword in dim_info["keywords"]:
                if keyword.lower() in content:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_dimension = {
                    "key": dim_key,
                    "name": dim_info["name"],
                    "icon": dim_info["icon"],
                    "priority_boost": dim_info["priority_boost"],
                }
        
        if best_dimension is None:
            best_dimension = {
                "key": "other",
                "name": "其他动态",
                "icon": "📰",
                "priority_boost": 0,
            }
        
        return best_dimension
    
    def _evaluate_importance(self, item: Dict) -> Dict:
        """评估新闻重要性"""
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        content = f"{title} {summary}"
        
        high_count = sum(1 for kw in self.high_importance_keywords if kw.lower() in content)
        medium_count = sum(1 for kw in self.medium_importance_keywords if kw.lower() in content)
        
        # 重点公司加分
        company_mentions = sum(1 for c in self.key_companies if c.lower() in content)
        
        # 计算总分
        score = high_count * 10 + medium_count * 5 + company_mentions * 3
        
        if score >= 25:
            level = "high"
            level_cn = "高"
            color = "#dc3545"
        elif score >= 12:
            level = "medium"
            level_cn = "中"
            color = "#fd7e14"
        else:
            level = "low"
            level_cn = "低"
            color = "#28a745"
        
        return {
            "level": level,
            "level_cn": level_cn,
            "score": score,
            "color": color,
        }
    
    def _extract_companies(self, item: Dict) -> List[str]:
        """提取关联的公司"""
        title = item.get("title", "")
        summary = item.get("summary", "")
        content = f"{title} {summary}"
        
        all_companies = (
            KEY_COMPANIES["international"] + 
            KEY_COMPANIES["domestic"] + 
            KEY_COMPANIES["applications"]
        )
        
        mentioned = [c for c in all_companies if c in content]
        return mentioned[:5]  # 最多返回5个
    
    def _generate_brief_comment(self, item: Dict) -> str:
        """为每条新闻生成简短小评"""
        title = item.get("title", "")
        summary = item.get("summary", "")
        content = f"{title} {summary}".lower()
        
        dimension = item.get("dimension", {})
        importance = item.get("importance", {})
        companies = item.get("companies", [])
        is_new = item.get("is_new", False)
        
        dim_name = dimension.get("name", "其他")
        imp_level = importance.get("level", "low")
        
        # 根据维度和重要性生成评语
        if dim_name == "技术突破":
            if imp_level == "high":
                if companies:
                    comment = f"⚡ 高价值 | {companies[0]}技术突破，具有行业标杆意义"
                else:
                    comment = "⚡ 高价值 | 重要技术突破，值得深入关注"
            else:
                comment = "🔬 技术进展 | 技术演进动态，保持关注"
        
        elif dim_name == "产品发布":
            if imp_level == "high":
                if companies:
                    comment = f"🚀 重要发布 | {companies[0]}新品发布，可能影响行业格局"
                else:
                    comment = "🚀 重要发布 | 重磅产品发布，建议关注"
            else:
                comment = "📦 产品更新 | 产品迭代动态"
        
        elif dim_name == "商业动态":
            if "融资" in content:
                comment = "💰 融资动态 | 资本市场信号，关注投资趋势"
            elif "收购" in content:
                comment = "🤝 收购动态 | 行业整合信号"
            else:
                comment = "💼 商业动态 | 商业合作/战略变化"
        
        elif dim_name == "开源生态":
            comment = "📦 开源动态 | 开源生态进展，技术人员可关注"
        
        elif dim_name == "政策监管":
            if imp_level == "high":
                comment = "⚠️ 重要政策 | 监管政策变化，可能影响行业发展"
            else:
                comment = "📜 政策动态 | 政策信息，保持了解"
        
        elif dim_name == "应用落地":
            comment = "🎯 应用案例 | AI落地实践，可参考借鉴"
        
        else:
            if imp_level == "high":
                comment = "📰 值得关注 | 重要行业动态"
            else:
                comment = "📋 行业资讯 | 一般性动态"
        
        # 添加新旧标记
        if is_new:
            comment = f"[新] {comment}"
        
        return comment
    
    def _calculate_priority(self, item: Dict) -> str:
        """计算综合优先级"""
        value_score = item.get("value_score", 50)
        importance = item.get("importance", {})
        dimension = item.get("dimension", {})
        is_new = item.get("is_new", False)
        
        imp_score = importance.get("score", 0)
        dim_boost = dimension.get("priority_boost", 0)
        
        # 综合分数
        total_score = value_score * 0.4 + imp_score * 0.3 + dim_boost + (20 if is_new else 0)
        
        if total_score >= 60:
            return "P1"  # 高优
        elif total_score >= 40:
            return "P2"  # 重要
        elif total_score >= 25:
            return "P3"  # 一般
        else:
            return "P4"  # 低优
    
    def _generate_executive_summary(self, items: List[Dict]) -> Dict:
        """生成执行摘要"""
        # 统计各维度数量
        dimension_counts = Counter(item.get("dimension", {}).get("name", "其他") for item in items)
        
        # 统计优先级分布
        priority_counts = Counter(item.get("priority", "P4") for item in items)
        
        # 提取热门公司
        all_companies = []
        for item in items:
            all_companies.extend(item.get("companies", []))
        hot_companies = [c for c, _ in Counter(all_companies).most_common(10)]
        
        # 统计新旧比例
        new_count = sum(1 for item in items if item.get("is_new", False))
        old_count = len(items) - new_count
        
        return {
            "dimension_counts": dict(dimension_counts),
            "priority_counts": dict(priority_counts),
            "hot_companies": hot_companies,
            "new_count": new_count,
            "old_count": old_count,
        }
    
    def _generate_expert_overview(self, items: List[Dict]) -> Dict:
        """生成专家总评"""
        total = len(items)
        if total == 0:
            return {
                "overview": "今日暂无重要AI动态。",
                "key_trends": [],
                "recommendations": [],
                "risk_level": "低",
                "risk_color": "#28a745",
            }
        
        # 统计
        p1_count = sum(1 for item in items if item.get("priority") == "P1")
        p2_count = sum(1 for item in items if item.get("priority") == "P2")
        new_count = sum(1 for item in items if item.get("is_new", False))
        
        # 热门维度
        dim_counter = Counter(item.get("dimension", {}).get("name", "") for item in items)
        top_dimensions = [d for d, _ in dim_counter.most_common(3)]
        
        # 热门公司
        all_companies = []
        for item in items:
            all_companies.extend(item.get("companies", []))
        company_counter = Counter(all_companies)
        top_companies = [c for c, _ in company_counter.most_common(5)]
        
        # 生成总评
        overview_parts = []
        
        # 开篇定调
        if p1_count >= 3:
            overview_parts.append(f"🔥 今日AI领域动态活跃：发现{p1_count}条高优信息，建议重点关注。")
            risk_level = "高"
            risk_color = "#dc3545"
        elif p1_count >= 1:
            overview_parts.append(f"📈 今日发现{p1_count}条高优信息，{p2_count}条重要信息，AI领域持续演进。")
            risk_level = "中"
            risk_color = "#fd7e14"
        else:
            overview_parts.append(f"📊 今日共监测到{total}条AI相关信息，整体态势平稳。")
            risk_level = "低"
            risk_color = "#28a745"
        
        # 热点方向
        if top_dimensions:
            overview_parts.append(f"今日热点方向：{', '.join(top_dimensions)}。")
        
        # 热门公司
        if top_companies:
            overview_parts.append(f"重点关注：{', '.join(top_companies[:3])}动态频繁。")
        
        # 关键趋势
        key_trends = []
        if "技术突破" in top_dimensions:
            key_trends.append("🔬 技术突破活跃：多个技术进展值得关注")
        if "产品发布" in top_dimensions:
            key_trends.append("🚀 产品密集发布：行业创新步伐加快")
        if "商业动态" in top_dimensions:
            key_trends.append("💼 资本市场活跃：投融资动态频繁")
        if "政策监管" in top_dimensions:
            key_trends.append("📜 政策风向变化：监管动态值得关注")
        
        if not key_trends:
            key_trends.append("📊 今日无显著趋势变化，市场相对平稳")
        
        # 核心建议
        recommendations = []
        if p1_count > 0:
            recommendations.append(f"⚡ 优先阅读{p1_count}条高优新闻，把握行业脉搏")
        if top_companies:
            recommendations.append(f"🎯 关注{top_companies[0]}最新动态")
        if new_count > total * 0.7:
            recommendations.append("📰 今日新信息较多，建议抽时间详读")
        
        if not recommendations:
            recommendations.append("✅ 今日态势平稳，保持常规关注即可")
        
        return {
            "overview": " ".join(overview_parts),
            "key_trends": key_trends[:4],
            "recommendations": recommendations[:4],
            "risk_level": risk_level,
            "risk_color": risk_color,
        }


# 便捷接口
def analyze_ai_news(collected_data: List[Dict]) -> Dict:
    """分析AI新闻的便捷接口"""
    analyzer = AIDataAnalyzer()
    return analyzer.analyze_all(collected_data)


if __name__ == "__main__":
    # 测试
    test_data = [
        {
            "title": "OpenAI发布GPT-5，性能大幅提升",
            "summary": "OpenAI今日正式发布GPT-5模型，在推理能力上取得重大突破",
            "value_score": 85,
            "is_new": True,
        },
        {
            "title": "百度文心一言4.0更新",
            "summary": "百度文心一言发布4.0版本，新增多项功能",
            "value_score": 65,
            "is_new": True,
        },
    ]
    
    results = analyze_ai_news(test_data)
    print(f"\n分析结果：{results['total_items']}条")
    print(f"专家总评：{results['expert_overview']['overview']}")
