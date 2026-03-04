# -*- coding: utf-8 -*-
"""
零售日报系统 - 数据分析模块（增强版）
按行业分类：即时零售、便利店、生鲜零售、折扣、商超、商圈、免税、烟草等
包含专业点评：整体点评、行业点评、新闻点评
"""
import sys
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import KEY_COMPANIES


class RetailDataAnalyzer:
    """零售日报数据分析器（专业版）"""
    
    def __init__(self):
        self._init_industry_system()
        self._init_importance_rules()
    
    def _init_industry_system(self):
        """初始化行业分类体系"""
        self.industries = {
            "instant_retail": {
                "name": "即时零售",
                "icon": "⚡",
                "keywords": ["即时零售", "闪购", "小时达", "同城配送", "即配", "到家", 
                            "美团买菜", "京东到家", "饿了么", "淘鲜达", "叮咚买菜", "朴朴"],
                "priority_boost": 18,
                "description": "本地生活O2O、即时配送相关",
            },
            "convenience": {
                "name": "便利店",
                "icon": "🏪",
                "keywords": ["便利店", "7-11", "全家", "罗森", "便利蜂", "美宜佳", 
                            "Today", "见福", "天福", "红旗连锁", "24小时", "鲜食"],
                "priority_boost": 15,
                "description": "便利店业态、鲜食、便利服务",
            },
            "fresh_retail": {
                "name": "生鲜零售",
                "icon": "🥬",
                "keywords": ["生鲜", "盒马", "叮咚", "每日优鲜", "钱大妈", "谊品", 
                            "前置仓", "菜市场", "菜篮子", "水果店", "鲜丰水果"],
                "priority_boost": 15,
                "description": "生鲜电商、社区生鲜、水果连锁",
            },
            "discount": {
                "name": "折扣零售",
                "icon": "💰",
                "keywords": ["折扣", "好特卖", "嗨特购", "奥特乐", "零食很忙", 
                            "赵一鸣", "临期", "尾货", "低价", "硬折扣", "软折扣"],
                "priority_boost": 18,
                "description": "折扣店、零食店、临期食品",
            },
            "supermarket": {
                "name": "商超",
                "icon": "🛒",
                "keywords": ["超市", "大卖场", "永辉", "大润发", "沃尔玛", "华润万家",
                            "物美", "联华", "家乐福", "世纪联华", "步步高", "人人乐"],
                "priority_boost": 12,
                "description": "大型超市、卖场、综合零售",
            },
            "membership": {
                "name": "会员店",
                "icon": "🎫",
                "keywords": ["会员店", "山姆", "Costco", "开市客", "麦德龙", "fudi",
                            "盒马X会员店", "会员制", "仓储式"],
                "priority_boost": 18,
                "description": "仓储会员店、付费会员零售",
            },
            "mall_district": {
                "name": "商圈/购物中心",
                "icon": "🏬",
                "keywords": ["商圈", "购物中心", "百货", "万达", "太古里", "SKP",
                            "恒隆", "大悦城", "印象城", "万象城", "龙湖天街"],
                "priority_boost": 10,
                "description": "购物中心、百货、商业地产",
            },
            "duty_free": {
                "name": "免税",
                "icon": "✈️",
                "keywords": ["免税", "离岛免税", "市内免税", "中免", "海免", "深免",
                            "日上", "DFS", "出境退税", "保税"],
                "priority_boost": 15,
                "description": "免税零售、跨境消费",
            },
            "tobacco": {
                "name": "烟草零售",
                "icon": "🚬",
                "keywords": ["烟草", "烟酒", "卷烟", "电子烟", "悦刻", "雪茄",
                            "烟草零售", "专卖店"],
                "priority_boost": 12,
                "description": "烟草销售、电子烟",
            },
            "community": {
                "name": "社区团购",
                "icon": "👥",
                "keywords": ["社区团购", "团长", "自提点", "多多买菜", "美团优选",
                            "淘菜菜", "兴盛优选", "团购"],
                "priority_boost": 12,
                "description": "社区团购、预售自提",
            },
            "specialty": {
                "name": "专业零售",
                "icon": "🎯",
                "keywords": ["母婴", "孩子王", "宠物", "药店", "名创优品", "无印良品",
                            "优衣库", "屈臣氏", "丝芙兰", "眼镜店"],
                "priority_boost": 10,
                "description": "垂直品类专业店",
            },
            "tech_retail": {
                "name": "零售科技",
                "icon": "🤖",
                "keywords": ["无人店", "智能货柜", "RFID", "电子价签", "自助结账",
                            "数字化", "智慧零售", "AI零售"],
                "priority_boost": 12,
                "description": "零售科技、数字化转型",
            },
        }
        
        # 事件类型
        self.event_types = {
            "expansion": {"name": "开店扩张", "icon": "📈", "keywords": ["开业", "开店", "新店", "首店", "扩张", "进驻"]},
            "contraction": {"name": "闭店收缩", "icon": "📉", "keywords": ["关店", "闭店", "撤出", "退出", "收缩"]},
            "investment": {"name": "融资并购", "icon": "💵", "keywords": ["融资", "收购", "并购", "投资", "上市", "IPO"]},
            "innovation": {"name": "业态创新", "icon": "💡", "keywords": ["新业态", "创新", "升级", "转型", "新模式"]},
            "supply_chain": {"name": "供应链", "icon": "📦", "keywords": ["供应链", "仓储", "物流", "配送", "自有品牌"]},
        }
    
    def _init_importance_rules(self):
        """初始化重要性评估规则"""
        self.high_importance_keywords = [
            "开业", "关店", "首店", "旗舰店", "融资", "收购", "并购",
            "扩张", "撤出", "战略", "独家", "重磅", "破产", "裁员",
        ]
        self.medium_importance_keywords = [
            "合作", "新品", "升级", "促销", "会员", "数字化", "试点",
        ]
        self.key_companies = (
            KEY_COMPANIES.get("convenience", []) + KEY_COMPANIES.get("supermarket", []) +
            KEY_COMPANIES.get("membership", []) + KEY_COMPANIES.get("discount", []) +
            KEY_COMPANIES.get("ecommerce", [])
        )
    
    def analyze_all(self, collected_data: List[Dict]) -> Dict[str, Any]:
        """执行全面分析"""
        print("\n📊 开始数据分析...")
        analyzed_items = []
        
        for item in collected_data:
            # 行业分类
            industry = self._classify_industry(item)
            item["industry"] = industry
            
            # 事件类型
            event_type = self._classify_event_type(item)
            item["event_type"] = event_type
            
            # 重要性评估
            importance = self._evaluate_importance(item)
            item["importance"] = importance
            
            # 提取公司
            companies = self._extract_companies(item)
            item["companies"] = companies
            
            # 生成专家点评
            expert_comment = self._generate_expert_comment(item)
            item["expert_comment"] = expert_comment
            
            # 简短点评（兼容旧字段）
            item["brief_comment"] = expert_comment.get("brief", "")
            item["dimension"] = {"name": industry["name"], "icon": industry["icon"], "key": industry["key"]}
            
            # 计算优先级
            priority = self._calculate_priority(item)
            item["priority"] = priority
            
            analyzed_items.append(item)
        
        # 按行业分组
        industry_groups = self._group_by_industry(analyzed_items)
        
        # 生成三层点评
        overall_review = self._generate_overall_review(analyzed_items, industry_groups)
        industry_reviews = self._generate_industry_reviews(industry_groups)
        
        print(f"   ✓ 分析完成，共{len(analyzed_items)}条")
        
        return {
            "items": analyzed_items,
            "industry_groups": industry_groups,
            "overall_review": overall_review,
            "industry_reviews": industry_reviews,
            "summary": self._generate_summary(analyzed_items),
            "expert_overview": overall_review,  # 兼容
            "total_items": len(analyzed_items),
        }
    
    def _classify_industry(self, item: Dict) -> Dict:
        """行业分类"""
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        content = f"{title} {summary}"
        
        best_industry = None
        best_score = 0
        
        for ind_key, ind_info in self.industries.items():
            score = sum(2 if kw.lower() in content else 0 for kw in ind_info["keywords"])
            if score > best_score:
                best_score = score
                best_industry = {
                    "key": ind_key,
                    "name": ind_info["name"],
                    "icon": ind_info["icon"],
                    "description": ind_info["description"],
                    "priority_boost": ind_info["priority_boost"],
                }
        
        if best_industry is None:
            best_industry = {"key": "other", "name": "其他零售", "icon": "📰", "description": "其他零售动态", "priority_boost": 0}
        
        return best_industry
    
    def _classify_event_type(self, item: Dict) -> Dict:
        """事件类型分类"""
        content = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        
        for evt_key, evt_info in self.event_types.items():
            if any(kw in content for kw in evt_info["keywords"]):
                return {"key": evt_key, "name": evt_info["name"], "icon": evt_info["icon"]}
        
        return {"key": "news", "name": "行业动态", "icon": "📋"}
    
    def _evaluate_importance(self, item: Dict) -> Dict:
        """评估重要性"""
        content = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        
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
        """提取关联公司"""
        content = f"{item.get('title', '')} {item.get('summary', '')}"
        all_companies = []
        for cat in KEY_COMPANIES.values():
            all_companies.extend(cat)
        return [c for c in all_companies if c in content][:5]
    
    def _generate_expert_comment(self, item: Dict) -> Dict:
        """生成专家点评"""
        title = item.get("title", "")
        industry = item.get("industry", {})
        event_type = item.get("event_type", {})
        importance = item.get("importance", {})
        companies = item.get("companies", [])
        
        ind_name = industry.get("name", "零售")
        evt_name = event_type.get("name", "动态")
        imp_level = importance.get("level", "low")
        
        # 关注点
        focus_points = []
        if "开" in evt_name or "扩" in evt_name:
            focus_points.append("市场扩张信号")
        if "关" in evt_name or "闭" in evt_name:
            focus_points.append("市场收缩信号")
        if "融资" in evt_name or "并购" in evt_name:
            focus_points.append("资本流向变化")
        if "创新" in evt_name:
            focus_points.append("业态创新趋势")
        
        # 原因分析
        reasons = []
        if companies:
            reasons.append(f"{companies[0]}作为行业代表，其动向反映行业趋势")
        if imp_level == "high":
            reasons.append("涉及重大战略调整或市场变化")
        if ind_name in ["即时零售", "折扣零售", "会员店"]:
            reasons.append(f"{ind_name}是当前零售热点赛道")
        
        # 简要点评
        if imp_level == "high":
            brief = f"🔥 {ind_name}重点 | {evt_name}，建议深入关注"
        elif imp_level == "medium":
            brief = f"📌 {ind_name} | {evt_name}动态"
        else:
            brief = f"📋 {ind_name} | 常规{evt_name}"
        
        return {
            "brief": brief,
            "focus_points": focus_points if focus_points else ["行业动态跟踪"],
            "reasons": reasons if reasons else ["保持对行业的常规关注"],
            "industry": ind_name,
            "event": evt_name,
        }
    
    def _calculate_priority(self, item: Dict) -> str:
        """计算优先级"""
        value_score = item.get("value_score", 50)
        importance = item.get("importance", {})
        industry = item.get("industry", {})
        is_new = item.get("is_new", False)
        
        total_score = (
            value_score * 0.4 +
            importance.get("score", 0) * 0.3 +
            industry.get("priority_boost", 0) +
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
    
    def _group_by_industry(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """按行业分组"""
        groups = defaultdict(list)
        for item in items:
            ind_key = item.get("industry", {}).get("key", "other")
            groups[ind_key].append(item)
        
        # 按P1数量排序
        sorted_groups = {}
        for key in sorted(groups.keys(), key=lambda k: -sum(1 for i in groups[k] if i.get("priority") == "P1")):
            sorted_groups[key] = sorted(groups[key], key=lambda x: (
                0 if x.get("priority") == "P1" else 1 if x.get("priority") == "P2" else 2,
                -x.get("importance", {}).get("score", 0)
            ))
        
        return sorted_groups
    
    def _generate_overall_review(self, items: List[Dict], industry_groups: Dict) -> Dict:
        """生成整体点评"""
        total = len(items)
        if total == 0:
            return {
                "overview": "今日暂无重要零售动态。",
                "focus_points": [],
                "reasons": [],
                "key_trends": [],
                "recommendations": [],
                "risk_level": "低",
                "risk_color": "#28a745",
            }
        
        p1_count = sum(1 for item in items if item.get("priority") == "P1")
        p2_count = sum(1 for item in items if item.get("priority") == "P2")
        
        # 热门行业
        industry_counter = Counter(item.get("industry", {}).get("name", "") for item in items)
        top_industries = [ind for ind, _ in industry_counter.most_common(4)]
        
        # 热门公司
        all_companies = []
        for item in items:
            all_companies.extend(item.get("companies", []))
        top_companies = [c for c, _ in Counter(all_companies).most_common(5)]
        
        # 事件类型分布
        event_counter = Counter(item.get("event_type", {}).get("name", "") for item in items)
        
        # === 生成专业点评 ===
        focus_points = []
        reasons = []
        
        # 1. 开店vs关店
        expansion_count = sum(1 for i in items if i.get("event_type", {}).get("key") == "expansion")
        contraction_count = sum(1 for i in items if i.get("event_type", {}).get("key") == "contraction")
        
        if expansion_count > contraction_count * 2:
            focus_points.append("零售扩张势头明显，行业整体向好")
            reasons.append(f"开店动态({expansion_count}条)远超关店({contraction_count}条)")
        elif contraction_count > expansion_count:
            focus_points.append("⚠️ 关店信号增多，需关注行业调整")
            reasons.append(f"关店信息({contraction_count}条)多于开店({expansion_count}条)")
        
        # 2. 热门赛道
        hot_tracks = []
        if "即时零售" in top_industries:
            hot_tracks.append("即时零售")
            focus_points.append("即时零售持续火热，本地生活竞争加剧")
        if "折扣零售" in top_industries:
            hot_tracks.append("折扣零售")
            focus_points.append("折扣零售热度不减，性价比消费成趋势")
        if "会员店" in top_industries:
            hot_tracks.append("会员店")
            focus_points.append("会员店赛道活跃，中产消费需求旺盛")
        
        if hot_tracks:
            reasons.append(f"今日热门赛道：{', '.join(hot_tracks)}")
        
        # 3. 重点公司
        if top_companies:
            focus_points.append(f"重点关注：{', '.join(top_companies[:3])}")
            reasons.append("头部企业动向往往引领行业趋势")
        
        # 概览文本
        if p1_count >= 3:
            overview = f"🔥 今日零售行业动态活跃：发现{p1_count}条高优信息，{p2_count}条重要信息。热点集中在{', '.join(top_industries[:2])}。"
            risk_level = "高"
            risk_color = "#dc3545"
        elif p1_count >= 1:
            overview = f"📈 今日发现{p1_count}条高优、{p2_count}条重要信息。{', '.join(top_industries[:2])}值得关注。"
            risk_level = "中"
            risk_color = "#fd7e14"
        else:
            overview = f"📊 今日共{total}条零售资讯，整体平稳。主要涉及{', '.join(top_industries[:2])}。"
            risk_level = "低"
            risk_color = "#28a745"
        
        # 建议
        recommendations = []
        if p1_count > 0:
            recommendations.append(f"⚡ 优先阅读{p1_count}条高优新闻")
        if "融资并购" in [e for e, _ in event_counter.most_common(3)]:
            recommendations.append("💰 关注资本动向，可能有行业整合")
        if contraction_count > 3:
            recommendations.append("⚠️ 留意闭店趋势，评估市场风险")
        
        return {
            "overview": overview,
            "focus_points": focus_points[:5],
            "reasons": reasons[:5],
            "key_trends": [f"{ind}: {cnt}条" for ind, cnt in industry_counter.most_common(4)],
            "recommendations": recommendations[:4],
            "risk_level": risk_level,
            "risk_color": risk_color,
            "top_industries": top_industries,
            "top_companies": top_companies,
        }
    
    def _generate_industry_reviews(self, industry_groups: Dict) -> Dict[str, Dict]:
        """生成各行业点评"""
        reviews = {}
        
        for ind_key, items in industry_groups.items():
            if not items:
                continue
            
            ind_info = self.industries.get(ind_key, {"name": "其他", "icon": "📰"})
            ind_name = ind_info.get("name", "其他")
            
            p1_items = [i for i in items if i.get("priority") == "P1"]
            p2_items = [i for i in items if i.get("priority") == "P2"]
            
            # 提取该行业的公司
            all_companies = []
            for item in items:
                all_companies.extend(item.get("companies", []))
            top_companies = [c for c, _ in Counter(all_companies).most_common(3)]
            
            # 事件分布
            events = Counter(i.get("event_type", {}).get("name", "") for i in items)
            
            # 关注点
            focus_points = []
            reasons = []
            
            if p1_items:
                focus_points.append(f"有{len(p1_items)}条高优信息，建议重点关注")
                reasons.append("涉及重大行业变化或头部企业动态")
            
            if events.get("开店扩张", 0) > 0:
                focus_points.append(f"开店动态活跃（{events.get('开店扩张', 0)}条）")
            if events.get("闭店收缩", 0) > 0:
                focus_points.append(f"⚠️ 有闭店信号（{events.get('闭店收缩', 0)}条）")
            if events.get("融资并购", 0) > 0:
                focus_points.append(f"资本动态频繁（{events.get('融资并购', 0)}条）")
            
            if top_companies:
                reasons.append(f"涉及企业：{', '.join(top_companies)}")
            
            # 行业评语
            if ind_key == "instant_retail":
                summary = "即时零售是当前零售最热赛道，美团、京东、阿里激烈竞争"
            elif ind_key == "discount":
                summary = "折扣零售契合消费降级趋势，零食店、硬折扣持续扩张"
            elif ind_key == "membership":
                summary = "会员店瞄准中产消费，山姆、Costco带动行业升级"
            elif ind_key == "fresh_retail":
                summary = "生鲜零售进入精细化运营阶段，前置仓模式持续优化"
            elif ind_key == "convenience":
                summary = "便利店业态成熟稳定，鲜食能力成核心竞争力"
            else:
                summary = f"{ind_name}行业动态"
            
            reviews[ind_key] = {
                "name": ind_name,
                "icon": ind_info.get("icon", "📰"),
                "total": len(items),
                "p1_count": len(p1_items),
                "p2_count": len(p2_items),
                "summary": summary,
                "focus_points": focus_points[:3],
                "reasons": reasons[:3],
                "top_companies": top_companies,
                "top_items": items[:5],
            }
        
        return reviews
    
    def _generate_summary(self, items: List[Dict]) -> Dict:
        """生成摘要统计"""
        dimension_counts = Counter(item.get("industry", {}).get("name", "其他") for item in items)
        priority_counts = Counter(item.get("priority", "P4") for item in items)
        
        all_companies = []
        for item in items:
            all_companies.extend(item.get("companies", []))
        
        return {
            "dimension_counts": dict(dimension_counts),
            "priority_counts": dict(priority_counts),
            "hot_companies": [c for c, _ in Counter(all_companies).most_common(10)],
            "new_count": sum(1 for item in items if item.get("is_new", False)),
            "old_count": sum(1 for item in items if not item.get("is_new", False)),
        }


def analyze_retail_news(collected_data: List[Dict]) -> Dict:
    return RetailDataAnalyzer().analyze_all(collected_data)
