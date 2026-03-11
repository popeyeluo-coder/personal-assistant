# -*- coding: utf-8 -*-
"""
AI日报系统 - 数据分析模块（增强版）
按AI产业链分类：硬件/芯片、基础模型、开发工具、应用层、投融资、政策监管
包含专业点评：整体点评、产业链点评、新闻点评
"""
import sys
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import KEY_COMPANIES


class AIDataAnalyzer:
    """AI日报数据分析器（专业版 + OpenClaw增强）"""
    
    def __init__(self, use_openclaw: bool = True):
        self._init_industry_chain()
        self._init_importance_rules()
        self.use_openclaw = use_openclaw
        self.openclaw_client = None
        
        if use_openclaw:
            try:
                from utils.openclaw_client import OpenClawClient
                self.openclaw_client = OpenClawClient()
                status = self.openclaw_client.check_gateway_status()
                if status["status"] == "running":
                    print("   ✓ OpenClaw 已连接，将使用AI增强分析")
                else:
                    print(f"   ⚠️ OpenClaw 未运行: {status['message']}")
                    self.openclaw_client = None
            except Exception as e:
                print(f"   ⚠️ OpenClaw 加载失败: {e}")
                self.openclaw_client = None
    
    def _init_industry_chain(self):
        """初始化AI产业链分类体系"""
        self.industry_chain = {
            "hardware": {
                "name": "硬件/芯片",
                "icon": "🔧",
                "keywords": ["芯片", "GPU", "TPU", "NPU", "NVIDIA", "英伟达", "AMD", "Intel",
                            "算力", "服务器", "数据中心", "H100", "H200", "B100", "A100",
                            "华为昇腾", "寒武纪", "算力卡", "AI加速器"],
                "priority_boost": 18,
                "description": "AI算力基础设施、芯片、硬件",
            },
            "foundation_model": {
                "name": "基础模型",
                "icon": "🧠",
                "keywords": ["大模型", "LLM", "GPT", "Claude", "Gemini", "Llama", "Qwen",
                            "文心", "混元", "通义", "GLM", "DeepSeek", "Mistral",
                            "多模态", "预训练", "参数", "benchmark", "开源模型"],
                "priority_boost": 20,
                "description": "大语言模型、多模态模型、基础能力",
            },
            "dev_tools": {
                "name": "开发工具/平台",
                "icon": "🛠️",
                "keywords": ["API", "SDK", "框架", "LangChain", "向量数据库", "RAG",
                            "Fine-tuning", "微调", "Prompt", "Agent", "开发平台",
                            "模型部署", "推理框架", "训练框架"],
                "priority_boost": 12,
                "description": "AI开发框架、工具链、平台",
            },
            "application": {
                "name": "应用层",
                "icon": "📱",
                "keywords": ["AI应用", "Copilot", "AI助手", "ChatBot", "AI绘画", "AI视频",
                            "AI音乐", "AI写作", "AI客服", "AI搜索", "Perplexity",
                            "Midjourney", "Sora", "Suno", "Character.AI"],
                "priority_boost": 15,
                "description": "面向用户的AI产品和应用",
            },
            "vertical": {
                "name": "垂直行业",
                "icon": "🏭",
                "keywords": ["AI医疗", "AI金融", "AI教育", "AI法律", "AI制造",
                            "自动驾驶", "机器人", "智能制造", "AI安防", "AI零售"],
                "priority_boost": 12,
                "description": "AI在各行业的落地应用",
            },
            "investment": {
                "name": "投融资",
                "icon": "💰",
                "keywords": ["融资", "投资", "估值", "IPO", "收购", "并购",
                            "独角兽", "VC", "天使轮", "A轮", "B轮"],
                "priority_boost": 15,
                "description": "AI领域资本动态",
            },
            "policy": {
                "name": "政策监管",
                "icon": "📜",
                "keywords": ["监管", "政策", "法规", "合规", "AI安全", "AI伦理",
                            "数据安全", "隐私", "审查", "备案", "治理"],
                "priority_boost": 15,
                "description": "AI相关政策法规动态",
            },
            "research": {
                "name": "学术研究",
                "icon": "📚",
                "keywords": ["论文", "研究", "实验", "学术", "科研", "算法",
                            "NeurIPS", "ICML", "ACL", "CVPR", "arxiv"],
                "priority_boost": 10,
                "description": "AI学术研究进展",
            },
        }
        
        # 事件类型
        self.event_types = {
            "release": {"name": "新品发布", "icon": "🚀", "keywords": ["发布", "上线", "推出", "开放", "公测"]},
            "breakthrough": {"name": "技术突破", "icon": "⚡", "keywords": ["突破", "创新", "首次", "领先", "超越"]},
            "funding": {"name": "融资动态", "icon": "💵", "keywords": ["融资", "投资", "估值", "收购", "并购"]},
            "opensource": {"name": "开源动态", "icon": "📦", "keywords": ["开源", "开放", "GitHub", "社区"]},
            "partnership": {"name": "合作签约", "icon": "🤝", "keywords": ["合作", "签约", "战略", "联盟"]},
        }
    
    def _init_importance_rules(self):
        """初始化重要性评估规则"""
        self.high_importance_keywords = [
            "突破", "首次", "重磅", "独家", "发布", "开源",
            "融资", "收购", "上线", "官宣", "GPT-5", "AGI",
            "超越", "领先", "创纪录", "里程碑",
        ]
        self.medium_importance_keywords = [
            "合作", "更新", "升级", "优化", "功能", "测试",
            "beta", "preview", "应用", "部署", "案例",
        ]
        self.key_companies = (
            KEY_COMPANIES.get("international", []) +
            KEY_COMPANIES.get("domestic", [])
        )
    
    def analyze_all(self, collected_data: List[Dict]) -> Dict[str, Any]:
        """执行全面分析"""
        print("\n📊 开始数据分析...")
        analyzed_items = []
        
        for item in collected_data:
            # 产业链分类
            chain = self._classify_chain(item)
            item["chain"] = chain
            
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
            
            # 兼容旧字段
            item["brief_comment"] = expert_comment.get("brief", "")
            item["dimension"] = {"name": chain["name"], "icon": chain["icon"], "key": chain["key"]}
            
            # 计算优先级
            priority = self._calculate_priority(item)
            item["priority"] = priority
            
            analyzed_items.append(item)
        
        # 按产业链分组
        chain_groups = self._group_by_chain(analyzed_items)
        
        # 生成三层点评
        overall_review = self._generate_overall_review(analyzed_items, chain_groups)
        chain_reviews = self._generate_chain_reviews(chain_groups)
        
        print(f"   ✓ 分析完成，共{len(analyzed_items)}条")
        
        result = {
            "items": analyzed_items,
            "chain_groups": chain_groups,
            "overall_review": overall_review,
            "chain_reviews": chain_reviews,
            "summary": self._generate_summary(analyzed_items),
            "expert_overview": overall_review,  # 兼容
            "total_items": len(analyzed_items),
        }
        
        # OpenClaw 增强分析
        if self.openclaw_client and len(analyzed_items) > 0:
            try:
                print("   🦞 OpenClaw 增强分析中...")
                openclaw_insights = self._openclaw_enhance(analyzed_items, overall_review)
                if openclaw_insights:
                    result["openclaw_insights"] = openclaw_insights
                    # 合并到整体点评中
                    if "ai_summary" in openclaw_insights:
                        result["overall_review"]["ai_summary"] = openclaw_insights["ai_summary"]
                    if "ai_recommendations" in openclaw_insights:
                        result["overall_review"]["ai_recommendations"] = openclaw_insights["ai_recommendations"]
                    print("   ✓ OpenClaw 增强完成")
            except Exception as e:
                print(f"   ⚠️ OpenClaw 增强失败: {e}")
        
        return result
    
    def _classify_chain(self, item: Dict) -> Dict:
        """产业链分类"""
        title = item.get("title", "").lower()
        summary = item.get("summary", "").lower()
        content = f"{title} {summary}"
        
        best_chain = None
        best_score = 0
        
        for chain_key, chain_info in self.industry_chain.items():
            score = sum(2 if kw.lower() in content else 0 for kw in chain_info["keywords"])
            if score > best_score:
                best_score = score
                best_chain = {
                    "key": chain_key,
                    "name": chain_info["name"],
                    "icon": chain_info["icon"],
                    "description": chain_info["description"],
                    "priority_boost": chain_info["priority_boost"],
                }
        
        if best_chain is None:
            best_chain = {"key": "other", "name": "其他AI动态", "icon": "📰", "description": "其他AI相关", "priority_boost": 0}
        
        return best_chain
    
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
        chain = item.get("chain", {})
        event_type = item.get("event_type", {})
        importance = item.get("importance", {})
        companies = item.get("companies", [])
        
        chain_name = chain.get("name", "AI")
        evt_name = event_type.get("name", "动态")
        imp_level = importance.get("level", "low")
        
        # 关注点
        focus_points = []
        if chain_name == "基础模型":
            focus_points.append("模型能力进展，可能影响下游应用")
        elif chain_name == "硬件/芯片":
            focus_points.append("算力供给变化，影响AI发展瓶颈")
        elif chain_name == "应用层":
            focus_points.append("产品形态创新，用户价值变化")
        elif chain_name == "投融资":
            focus_points.append("资本流向，反映市场热点和趋势")
        elif chain_name == "政策监管":
            focus_points.append("政策风向，可能影响业务合规")
        
        if "发布" in evt_name or "开源" in evt_name:
            focus_points.append("新产品/技术，评估应用价值")
        if "融资" in evt_name:
            focus_points.append("资本认可度，行业竞争格局")
        
        # 原因分析
        reasons = []
        if companies:
            reasons.append(f"{companies[0]}是AI行业关键玩家，动向值得关注")
        if imp_level == "high":
            reasons.append("涉及重大技术突破或战略调整")
        if chain_name in ["基础模型", "硬件/芯片"]:
            reasons.append(f"{chain_name}是AI产业链核心环节")
        
        # 简要点评
        if imp_level == "high":
            brief = f"🔥 {chain_name}重点 | {evt_name}，建议深入关注"
        elif imp_level == "medium":
            brief = f"📌 {chain_name} | {evt_name}动态"
        else:
            brief = f"📋 {chain_name} | 常规{evt_name}"
        
        return {
            "brief": brief,
            "focus_points": focus_points if focus_points else ["AI行业动态跟踪"],
            "reasons": reasons if reasons else ["保持对AI领域的常规关注"],
            "chain": chain_name,
            "event": evt_name,
        }
    
    def _calculate_priority(self, item: Dict) -> str:
        """计算优先级"""
        value_score = item.get("value_score", 50)
        importance = item.get("importance", {})
        chain = item.get("chain", {})
        is_new = item.get("is_new", False)
        
        total_score = (
            value_score * 0.4 +
            importance.get("score", 0) * 0.3 +
            chain.get("priority_boost", 0) +
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
    
    def _group_by_chain(self, items: List[Dict]) -> Dict[str, List[Dict]]:
        """按产业链分组"""
        groups = defaultdict(list)
        for item in items:
            chain_key = item.get("chain", {}).get("key", "other")
            groups[chain_key].append(item)
        
        # 按P1数量排序
        sorted_groups = {}
        for key in sorted(groups.keys(), key=lambda k: -sum(1 for i in groups[k] if i.get("priority") == "P1")):
            sorted_groups[key] = sorted(groups[key], key=lambda x: (
                0 if x.get("priority") == "P1" else 1 if x.get("priority") == "P2" else 2,
                -x.get("importance", {}).get("score", 0)
            ))
        
        return sorted_groups
    
    def _generate_overall_review(self, items: List[Dict], chain_groups: Dict) -> Dict:
        """生成整体点评"""
        total = len(items)
        if total == 0:
            return {
                "overview": "今日暂无重要AI动态。",
                "focus_points": [],
                "reasons": [],
                "key_trends": [],
                "recommendations": [],
                "risk_level": "低",
                "risk_color": "#28a745",
            }
        
        p1_count = sum(1 for item in items if item.get("priority") == "P1")
        p2_count = sum(1 for item in items if item.get("priority") == "P2")
        
        # 热门产业链
        chain_counter = Counter(item.get("chain", {}).get("name", "") for item in items)
        top_chains = [c for c, _ in chain_counter.most_common(4)]
        
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
        
        # 1. 产业链热点
        if "基础模型" in top_chains:
            focus_points.append("大模型领域动态频繁，关注模型能力进展")
            reasons.append("基础模型是AI产业核心，影响整个生态")
        if "硬件/芯片" in top_chains:
            focus_points.append("算力/芯片有新动态，关注供给变化")
            reasons.append("算力是AI发展瓶颈，芯片格局影响深远")
        if "应用层" in top_chains:
            focus_points.append("AI应用活跃，关注产品创新和用户价值")
            reasons.append("应用层是AI价值变现的关键环节")
        if "投融资" in top_chains:
            focus_points.append("资本市场活跃，关注投资热点")
            reasons.append("融资动态反映市场信心和趋势判断")
        
        # 2. 重点公司
        if top_companies:
            focus_points.append(f"重点关注：{', '.join(top_companies[:3])}")
            reasons.append("头部企业动向引领行业发展方向")
        
        # 3. 事件类型
        if event_counter.get("新品发布", 0) > 2:
            focus_points.append("多个新品发布，AI产品迭代加速")
        if event_counter.get("技术突破", 0) > 0:
            focus_points.append("有技术突破报道，关注创新进展")
        
        # 概览文本
        if p1_count >= 3:
            overview = f"🔥 今日AI领域动态活跃：发现{p1_count}条高优信息，{p2_count}条重要信息。热点集中在{', '.join(top_chains[:2])}。"
            risk_level = "高"
            risk_color = "#dc3545"
        elif p1_count >= 1:
            overview = f"📈 今日发现{p1_count}条高优、{p2_count}条重要信息。{', '.join(top_chains[:2])}值得关注。"
            risk_level = "中"
            risk_color = "#fd7e14"
        else:
            overview = f"📊 今日共{total}条AI资讯，整体平稳。主要涉及{', '.join(top_chains[:2])}。"
            risk_level = "低"
            risk_color = "#28a745"
        
        # 建议
        recommendations = []
        if p1_count > 0:
            recommendations.append(f"⚡ 优先阅读{p1_count}条高优新闻，把握行业脉搏")
        if "基础模型" in top_chains:
            recommendations.append("🧠 关注大模型进展，评估对业务的影响")
        if top_companies:
            recommendations.append(f"🎯 关注{top_companies[0]}最新动态")
        
        return {
            "overview": overview,
            "focus_points": focus_points[:5],
            "reasons": reasons[:5],
            "key_trends": [f"{c}: {cnt}条" for c, cnt in chain_counter.most_common(4)],
            "recommendations": recommendations[:4],
            "risk_level": risk_level,
            "risk_color": risk_color,
            "top_chains": top_chains,
            "top_companies": top_companies,
        }
    
    def _generate_chain_reviews(self, chain_groups: Dict) -> Dict[str, Dict]:
        """生成各产业链点评"""
        reviews = {}
        
        for chain_key, items in chain_groups.items():
            if not items:
                continue
            
            chain_info = self.industry_chain.get(chain_key, {"name": "其他", "icon": "📰"})
            chain_name = chain_info.get("name", "其他")
            
            p1_items = [i for i in items if i.get("priority") == "P1"]
            p2_items = [i for i in items if i.get("priority") == "P2"]
            
            # 提取该产业链的公司
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
                reasons.append("涉及重大技术突破或战略调整")
            
            if events.get("新品发布", 0) > 0:
                focus_points.append(f"有新品发布动态（{events.get('新品发布', 0)}条）")
            if events.get("技术突破", 0) > 0:
                focus_points.append(f"有技术突破报道（{events.get('技术突破', 0)}条）")
            if events.get("融资动态", 0) > 0:
                focus_points.append(f"资本动态频繁（{events.get('融资动态', 0)}条）")
            
            if top_companies:
                reasons.append(f"涉及企业：{', '.join(top_companies)}")
            
            # 产业链评语
            if chain_key == "foundation_model":
                summary = "大模型是AI产业核心，OpenAI/Anthropic/国内厂商激烈竞争"
            elif chain_key == "hardware":
                summary = "AI芯片供需紧张，NVIDIA主导市场，国产替代加速"
            elif chain_key == "application":
                summary = "AI应用百花齐放，关注用户价值和商业化进展"
            elif chain_key == "investment":
                summary = "AI投资热度不减，关注估值变化和赛道选择"
            elif chain_key == "policy":
                summary = "全球AI监管趋严，合规要求提升"
            elif chain_key == "dev_tools":
                summary = "AI开发工具链成熟，Agent框架成新热点"
            else:
                summary = f"{chain_name}动态"
            
            reviews[chain_key] = {
                "name": chain_name,
                "icon": chain_info.get("icon", "📰"),
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
        dimension_counts = Counter(item.get("chain", {}).get("name", "其他") for item in items)
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
    
    def _openclaw_enhance(self, items: List[Dict], overall_review: Dict) -> Dict:
        """使用 OpenClaw 增强分析"""
        if not self.openclaw_client:
            return {}
        
        # 准备新闻摘要（只取高优和中优）
        priority_items = [i for i in items if i.get("priority") in ["P1", "P2"]][:15]
        if not priority_items:
            priority_items = items[:10]
        
        news_summary = "\n".join([
            f"- {i.get('title', '')} ({i.get('chain', {}).get('name', '')})"
            for i in priority_items
        ])
        
        # 获取整体点评
        existing_overview = overall_review.get("overview", "")
        top_chains = ", ".join(overall_review.get("top_chains", [])[:3])
        top_companies = ", ".join(overall_review.get("top_companies", [])[:3])
        
        prompt = f"""作为AI行业资深分析师，请基于今日AI行业新闻动态，提供简洁专业的分析总结。

今日AI新闻概要（{len(items)}条）：
{news_summary}

热门产业链：{top_chains}
活跃企业：{top_companies}

请提供：
1. 今日AI行业核心观点（2-3句话，突出最重要的趋势或事件）
2. 给从业者的建议（1-2条具体可执行的建议）

注意：直接给出分析内容，不要使用JSON格式，不要重复新闻标题。语言简洁有力。"""

        response = self.openclaw_client.chat_simple(prompt, timeout=60)
        
        if response:
            return {
                "ai_summary": response,
                "ai_recommendations": [],  # 可以进一步解析
                "model": "openclaw/deepseek-chat",
                "enhanced": True
            }
        
        return {}


def analyze_ai_news(collected_data: List[Dict]) -> Dict:
    return AIDataAnalyzer().analyze_all(collected_data)
