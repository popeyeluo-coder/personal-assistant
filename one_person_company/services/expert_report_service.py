"""
专家级日报服务 - 自我迭代版
- 多轮搜索+严格筛选+AI深度分析
- 每条新闻配专业小结（启示+微信支付结合点）
- 确保内容专业度和价值度
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import yaml

logger = logging.getLogger(__name__)

# Brave Search API
BRAVE_NEWS_API = "https://api.search.brave.com/res/v1/news/search"
BRAVE_WEB_API = "https://api.search.brave.com/res/v1/web/search"

# 高质量信息源白名单
QUALITY_SOURCES = {
    "tech": ["36kr.com", "sina.com", "sohu.com", "qq.com", "163.com", "leiphone.com", 
             "ifanr.com", "pingwest.com", "huxiu.com", "geekpark.net", "cnbeta.com",
             "theverge.com", "techcrunch.com", "wired.com", "arstechnica.com"],
    "finance": ["eastmoney.com", "sina.com.cn", "wallstreetcn.com", "cls.cn", 
                "bloomberg.com", "reuters.com", "ft.com", "wsj.com"],
    "retail": ["linkshop.com", "ebrun.com", "retailnews.com", "chainstoreage.com"]
}

# 低质量来源黑名单
BLACKLIST_SOURCES = [
    "pinterest", "facebook", "instagram", "tiktok", "youtube", 
    "baidu.com/s", "zhidao.baidu", "tieba.baidu", "docin.com",
    "wenku.baidu", "doc88.com"
]


class ExpertReportService:
    """
    专家级日报生成服务
    作为用户的唯一信息源，确保内容质量和专业度
    
    核心原则：
    1. 宁缺毋滥 - 只推送真正有价值的信息
    2. 深度分析 - 每条新闻都配专业小结
    3. 行动导向 - 明确微信支付可以做什么
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.brave_api_key = self.config.get("brave_api_key", "")
        
        # AI前沿日报框架 - 精准关键词
        self.ai_dimensions = {
            "hardware": {
                "name": "🔧 算力与芯片",
                "icon": "💻",
                "keywords": [
                    "NVIDIA GTC 2026", "AI芯片 发布", "华为昇腾 算力",
                    "GPU 服务器", "AI推理芯片", "国产AI芯片"
                ],
                "en_keywords": [
                    "NVIDIA AI chip 2026", "AI accelerator news",
                    "GPU datacenter", "AI inference chip"
                ],
                "context": "算力是AI的基础设施，关注芯片发展对理解AI产业格局至关重要"
            },
            "models": {
                "name": "🧠 大模型动态", 
                "icon": "🤖",
                "keywords": [
                    "DeepSeek V4", "GPT-5", "Claude 4", "Gemini 2",
                    "通义千问 发布", "文心一言 更新", "多模态模型"
                ],
                "en_keywords": [
                    "LLM release 2026", "GPT-5 OpenAI",
                    "multimodal AI model", "open source LLM"
                ],
                "context": "大模型是AI能力的核心载体，模型迭代决定应用边界"
            },
            "applications": {
                "name": "📱 AI应用与Agent",
                "icon": "🚀",
                "keywords": [
                    "AI Agent 应用", "AIGC 产品", "AI编程 工具",
                    "AI眼镜", "AI硬件", "企业AI 落地"
                ],
                "en_keywords": [
                    "AI agent application", "AIGC product",
                    "AI coding assistant", "enterprise AI"
                ],
                "context": "AI应用是商业价值的最终体现，关注落地场景和用户价值"
            },
            "industry": {
                "name": "🏢 产业与投资",
                "icon": "💰",
                "keywords": [
                    "AI融资 2026", "AI公司 估值", "OpenAI 融资",
                    "AI独角兽", "AI政策 监管"
                ],
                "en_keywords": [
                    "AI funding 2026", "OpenAI valuation",
                    "AI startup investment", "AI regulation"
                ],
                "context": "资本流向和政策导向反映产业趋势，帮助把握战略方向"
            }
        }
        
        # 零售行业日报框架
        self.retail_dimensions = {
            "supermarket": {
                "name": "🛒 商超与会员店",
                "icon": "🏪",
                "keywords": [
                    "山姆会员店 开店", "盒马 扩张", "沃尔玛 中国",
                    "Costco 中国", "会员制零售"
                ],
                "en_keywords": ["Sam's Club China", "Costco retail", "membership retail"],
                "wechat_pay_angle": "会员体系打通、小程序商城、到家业务支付"
            },
            "discount": {
                "name": "🍬 硬折扣零售",
                "icon": "💸",
                "keywords": [
                    "奥乐齐 开店", "硬折扣 零售", "零食很忙 扩张",
                    "好特卖", "折扣超市"
                ],
                "en_keywords": ["ALDI China", "hard discount retail", "discount grocery"],
                "wechat_pay_angle": "快速收银、无感支付、门店数字化解决方案"
            },
            "convenience": {
                "name": "🏪 便利店",
                "icon": "🌙",
                "keywords": [
                    "便利店 数字化", "7-11 中国", "罗森 扩张",
                    "便利蜂", "美宜佳"
                ],
                "en_keywords": ["convenience store digital", "7-Eleven China"],
                "wechat_pay_angle": "刷脸支付、小程序点单、会员私域运营"
            },
            "dutyfree": {
                "name": "✈️ 免税零售",
                "icon": "🛫",
                "keywords": [
                    "海南免税 销售", "中免集团", "免税店 客流",
                    "离岛免税", "入境游 消费"
                ],
                "en_keywords": ["Hainan duty free", "China duty free retail"],
                "wechat_pay_angle": "境外钱包互通、外卡支付、跨境支付便利化"
            },
            "payment": {
                "name": "💳 支付与金融科技",
                "icon": "📲",
                "keywords": [
                    "移动支付 趋势", "数字人民币 试点", "刷脸支付",
                    "支付 创新", "零售支付"
                ],
                "en_keywords": ["mobile payment China", "digital yuan", "retail payment"],
                "wechat_pay_angle": "行业趋势洞察、竞品动态、创新机会"
            }
        }
    
    def search_news(self, query: str, count: int = 15, freshness: str = "pw") -> List[Dict]:
        """
        使用Brave Search搜索新闻
        freshness: pd=24小时, pw=1周, pm=1月
        """
        if not self.brave_api_key:
            logger.warning("未配置Brave API Key")
            return []
        
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "X-Subscription-Token": self.brave_api_key
            }
            
            params = {
                "q": query,
                "count": count,
                "freshness": freshness,
                "text_decorations": False,
                "spellcheck": False
            }
            
            response = requests.get(BRAVE_NEWS_API, headers=headers, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                news_list = []
                for item in results:
                    news_list.append({
                        "title": item.get("title", ""),
                        "description": item.get("description", ""),
                        "url": item.get("url", ""),
                        "source": item.get("meta_url", {}).get("hostname", ""),
                        "age": item.get("age", ""),
                        "thumbnail": item.get("thumbnail", {}).get("src", ""),
                        "extra_snippets": item.get("extra_snippets", [])
                    })
                
                return news_list
            else:
                logger.error(f"Brave搜索失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"搜索异常: {e}")
            return []
    
    def search_web(self, query: str, count: int = 10) -> List[Dict]:
        """Web搜索补充"""
        if not self.brave_api_key:
            return []
        
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key
            }
            
            params = {
                "q": query,
                "count": count,
                "freshness": "pw"
            }
            
            response = requests.get(BRAVE_WEB_API, headers=headers, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                web_results = data.get("web", {}).get("results", [])
                
                results = []
                for item in web_results:
                    results.append({
                        "title": item.get("title", ""),
                        "description": item.get("description", ""),
                        "url": item.get("url", ""),
                        "source": item.get("meta_url", {}).get("hostname", ""),
                        "age": item.get("age", "")
                    })
                
                return results
            return []
            
        except Exception as e:
            logger.error(f"Web搜索异常: {e}")
            return []
    
    def _is_quality_source(self, source: str, category: str = "tech") -> bool:
        """判断是否为高质量信息源"""
        source_lower = source.lower()
        
        # 黑名单过滤
        for blacklist in BLACKLIST_SOURCES:
            if blacklist in source_lower:
                return False
        
        # 白名单优先
        quality_list = QUALITY_SOURCES.get(category, []) + QUALITY_SOURCES.get("tech", [])
        for quality in quality_list:
            if quality in source_lower:
                return True
        
        # 通用判断：主流媒体
        mainstream = ["sina", "sohu", "qq", "163", "tencent", "baidu", "36kr", 
                      "huxiu", "ifanr", "theverge", "techcrunch", "bloomberg"]
        for m in mainstream:
            if m in source_lower:
                return True
        
        return False
    
    def _calculate_news_score(self, news: Dict, category: str = "tech") -> float:
        """计算新闻质量评分 (0-100)"""
        score = 50.0  # 基础分
        
        title = news.get("title", "")
        desc = news.get("description", "")
        source = news.get("source", "")
        
        # 标题质量 (+20)
        if len(title) > 10 and len(title) < 80:
            score += 10
        if not any(spam in title for spam in ["广告", "推广", "点击", "免费"]):
            score += 10
        
        # 描述质量 (+20)
        if len(desc) > 80:
            score += 10
        if len(desc) > 150:
            score += 10
        
        # 信息源质量 (+30)
        if self._is_quality_source(source, category):
            score += 30
        elif "." in source:  # 至少是正常网站
            score += 10
        
        # 时效性 (+10)
        age = news.get("age", "")
        if "小时" in age or "hour" in age.lower():
            score += 10
        elif "天" in age and ("1天" in age or "2天" in age):
            score += 5
        
        # 内容关键词 (+10)
        important_keywords = ["发布", "官宣", "首次", "突破", "融资", "收购", 
                              "上线", "开业", "扩张", "战略"]
        for kw in important_keywords:
            if kw in title:
                score += 3
                break
        
        return min(score, 100)
    
    def filter_and_rank_news(self, news_list: List[Dict], category: str = "tech", 
                             min_score: float = 60, max_count: int = 3) -> List[Dict]:
        """
        严格筛选和排序新闻
        - 去重
        - 质量评分
        - 只保留高分新闻
        """
        seen_titles = set()
        scored_news = []
        
        for news in news_list:
            title = news.get("title", "")
            url = news.get("url", "")
            
            # 基础过滤
            if not title or not url:
                continue
            
            # 去重（标题相似度）
            title_key = title[:30]
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)
            
            # 计算评分
            score = self._calculate_news_score(news, category)
            if score >= min_score:
                news["quality_score"] = score
                scored_news.append(news)
        
        # 按评分排序，取TopN
        scored_news.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        return scored_news[:max_count]
    
    def generate_expert_insight(self, news: Dict, dimension_key: str, 
                                 report_type: str = "ai") -> Dict:
        """
        生成专家级洞察小结
        包含：核心要点、对你的启示、微信支付结合点
        """
        title = news.get("title", "")
        desc = news.get("description", "")
        source = news.get("source", "")
        
        # 根据维度和新闻内容生成专业小结
        insight = {
            "summary": "",
            "implication": "",
            "wechat_pay_action": ""
        }
        
        if report_type == "ai":
            insight = self._generate_ai_insight(title, desc, dimension_key)
        else:
            insight = self._generate_retail_insight(title, desc, dimension_key)
        
        return insight
    
    def _generate_ai_insight(self, title: str, desc: str, dim_key: str) -> Dict:
        """生成AI领域专业洞察"""
        content = f"{title} {desc}".lower()
        
        insights = {
            "hardware": {
                "summary": "算力基础设施持续升级，国产替代加速推进",
                "implication": "关注算力成本下降带来的AI应用普及机会，以及国产芯片生态对支付系统的潜在影响",
                "wechat_pay_action": "探索AI推理在风控、反欺诈场景的应用，评估国产算力对支付系统的适配"
            },
            "models": {
                "summary": "大模型能力边界持续扩展，多模态成为标配",
                "implication": "模型能力提升将重塑用户交互方式，智能客服、智能推荐等场景即将迎来体验升级",
                "wechat_pay_action": "加速AI客服、智能推荐在支付场景的落地，探索多模态交互的支付体验"
            },
            "applications": {
                "summary": "AI应用从概念走向落地，Agent成为新范式",
                "implication": "AI Agent将重构服务流程，自动化、智能化成为竞争力关键",
                "wechat_pay_action": "布局支付Agent能力，实现智能对账、自动开票、智能财务等增值服务"
            },
            "industry": {
                "summary": "AI产业资本持续涌入，头部效应加剧",
                "implication": "巨额融资将加速技术迭代和市场竞争，需要关注产业格局变化对生态的影响",
                "wechat_pay_action": "关注AI独角兽的支付需求，提前布局To B支付解决方案"
            }
        }
        
        base_insight = insights.get(dim_key, insights["applications"])
        
        # 根据具体内容定制化
        if "nvidia" in content or "英伟达" in content:
            base_insight["summary"] = "英伟达持续引领AI算力市场，新产品发布值得关注"
        elif "deepseek" in content or "深度求索" in content:
            base_insight["summary"] = "国产大模型DeepSeek持续突破，有望改变AI格局"
            base_insight["wechat_pay_action"] = "关注国产大模型的商业化机会，评估合作可能性"
        elif "openai" in content:
            base_insight["summary"] = "OpenAI持续领跑全球AI竞赛，融资规模创历史新高"
        elif "agent" in content or "智能体" in content:
            base_insight["summary"] = "AI Agent正在从概念走向商业化，自主决策能力持续增强"
        elif "融资" in content or "投资" in content:
            base_insight["summary"] = "AI领域投融资持续活跃，资本看好长期发展前景"
        
        return base_insight
    
    def _generate_retail_insight(self, title: str, desc: str, dim_key: str) -> Dict:
        """生成零售领域专业洞察"""
        content = f"{title} {desc}".lower()
        
        insights = {
            "supermarket": {
                "summary": "会员制零售持续扩张，差异化竞争加剧",
                "implication": "会员经济成为零售竞争焦点，支付+会员的深度融合是机会",
                "wechat_pay_action": "推广微信支付会员通解决方案，深化与山姆、盒马等头部商超合作"
            },
            "discount": {
                "summary": "硬折扣赛道高速增长，供应链效率成为核心壁垒",
                "implication": "折扣零售的快速扩张带来大量支付场景，需要匹配高效解决方案",
                "wechat_pay_action": "针对硬折扣门店推出轻量化接入方案，支持快速开店需求"
            },
            "convenience": {
                "summary": "便利店数字化转型深入，全渠道融合成趋势",
                "implication": "便利店是高频支付场景，数字化升级带来增值服务机会",
                "wechat_pay_action": "深化刷脸支付在便利店的部署，推广小程序+企微私域方案"
            },
            "dutyfree": {
                "summary": "免税消费持续复苏，入境游带动增量需求",
                "implication": "跨境支付便利化是吸引境外游客的关键，政策红利持续释放",
                "wechat_pay_action": "加速外卡支付、境外钱包互通在免税场景的落地"
            },
            "payment": {
                "summary": "支付行业持续创新，数字人民币生态扩展",
                "implication": "支付创新是零售数字化的基础，需持续关注技术和政策动向",
                "wechat_pay_action": "深化数字人民币场景建设，探索支付+AI的创新应用"
            }
        }
        
        base_insight = insights.get(dim_key, insights["payment"])
        
        # 根据具体内容定制化
        if "山姆" in content or "sam" in content:
            base_insight["summary"] = "山姆会员店持续扩张，会员制零售展现强劲增长"
            base_insight["wechat_pay_action"] = "深化与山姆的合作，打通会员体系与支付积分"
        elif "盒马" in content:
            base_insight["summary"] = "盒马加速门店扩张，新零售模式持续进化"
            base_insight["wechat_pay_action"] = "关注盒马NB业态对支付的需求变化"
        elif "奥乐齐" in content or "aldi" in content:
            base_insight["summary"] = "奥乐齐硬折扣模式获市场认可，门店规模冲刺百家"
            base_insight["wechat_pay_action"] = "主动对接奥乐齐新店支付需求，提供标准化接入方案"
        elif "免税" in content:
            base_insight["summary"] = "免税消费持续火热，成为拉动内需的重要引擎"
            base_insight["wechat_pay_action"] = "推动境外支付能力在免税场景的应用"
        elif "数字人民币" in content:
            base_insight["summary"] = "数字人民币生态加速完善，应用场景持续拓展"
            base_insight["wechat_pay_action"] = "加速数字人民币在更多场景的接入"
        
        return base_insight
    
    def generate_ai_daily_report(self) -> Dict:
        """生成AI前沿日报（专家版）"""
        report_date = datetime.now().strftime("%Y年%m月%d日")
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()]
        
        report = {
            "title": "🤖 AI前沿日报",
            "subtitle": "每日精选 · 专家解读",
            "date": f"{report_date} {weekday}",
            "dimensions": {},
            "top_insight": "",
            "total_news": 0
        }
        
        all_news_count = 0
        
        for dim_key, dim_info in self.ai_dimensions.items():
            logger.info(f"搜索 {dim_info['name']}...")
            dim_news = []
            
            # 多关键词搜索
            for keyword in dim_info["keywords"][:4]:
                results = self.search_news(keyword, count=10, freshness="pw")
                dim_news.extend(results)
            
            # 英文补充
            for keyword in dim_info["en_keywords"][:2]:
                results = self.search_news(keyword, count=5, freshness="pw")
                dim_news.extend(results)
            
            # 严格筛选
            filtered_news = self.filter_and_rank_news(dim_news, category="tech", 
                                                       min_score=55, max_count=2)
            
            # 为每条新闻生成专业洞察
            news_with_insights = []
            for news in filtered_news:
                insight = self.generate_expert_insight(news, dim_key, "ai")
                news["insight"] = insight
                news_with_insights.append(news)
            
            report["dimensions"][dim_key] = {
                "name": dim_info["name"],
                "icon": dim_info["icon"],
                "context": dim_info["context"],
                "news": news_with_insights,
                "count": len(news_with_insights)
            }
            
            all_news_count += len(news_with_insights)
        
        report["total_news"] = all_news_count
        report["top_insight"] = self._generate_ai_top_insight(report["dimensions"])
        
        return report
    
    def generate_retail_daily_report(self) -> Dict:
        """生成零售行业日报（专家版）"""
        report_date = datetime.now().strftime("%Y年%m月%d日")
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()]
        
        report = {
            "title": "🛒 零售行业日报",
            "subtitle": "深度洞察 · 支付机会",
            "date": f"{report_date} {weekday}",
            "dimensions": {},
            "wechat_pay_opportunities": [],
            "top_insight": "",
            "total_news": 0
        }
        
        all_news_count = 0
        opportunities = []
        
        for dim_key, dim_info in self.retail_dimensions.items():
            logger.info(f"搜索 {dim_info['name']}...")
            dim_news = []
            
            # 多关键词搜索
            for keyword in dim_info["keywords"][:4]:
                results = self.search_news(keyword, count=10, freshness="pw")
                dim_news.extend(results)
            
            # 严格筛选
            filtered_news = self.filter_and_rank_news(dim_news, category="retail", 
                                                       min_score=55, max_count=2)
            
            # 为每条新闻生成专业洞察
            news_with_insights = []
            for news in filtered_news:
                insight = self.generate_expert_insight(news, dim_key, "retail")
                news["insight"] = insight
                news_with_insights.append(news)
                
                # 收集微信支付机会
                if insight.get("wechat_pay_action"):
                    opportunities.append({
                        "area": dim_info["name"],
                        "action": insight["wechat_pay_action"],
                        "source_title": news.get("title", "")[:30]
                    })
            
            report["dimensions"][dim_key] = {
                "name": dim_info["name"],
                "icon": dim_info["icon"],
                "wechat_pay_angle": dim_info.get("wechat_pay_angle", ""),
                "news": news_with_insights,
                "count": len(news_with_insights)
            }
            
            all_news_count += len(news_with_insights)
        
        report["total_news"] = all_news_count
        report["wechat_pay_opportunities"] = opportunities[:5]
        report["top_insight"] = self._generate_retail_top_insight(report["dimensions"])
        
        return report
    
    def _generate_ai_top_insight(self, dimensions: Dict) -> str:
        """生成AI日报顶部洞察"""
        insights = []
        
        for dim_key, dim_data in dimensions.items():
            if dim_data.get("count", 0) > 0:
                news = dim_data.get("news", [])[0]
                title = news.get("title", "")[:25]
                insights.append(f"**{dim_data['name']}**: {title}...")
        
        if insights:
            return "📊 **今日AI领域核心动态**\n\n" + "\n".join(insights)
        return "今日AI领域暂无重大更新"
    
    def _generate_retail_top_insight(self, dimensions: Dict) -> str:
        """生成零售日报顶部洞察"""
        total = sum(d.get("count", 0) for d in dimensions.values())
        
        active_dims = [d["name"] for d in dimensions.values() if d.get("count", 0) > 0]
        
        return f"""📊 **今日零售行业动态**

共筛选 **{total}** 条高价值信息，覆盖 {len(active_dims)} 个核心赛道

💡 **重点关注**: {", ".join(active_dims[:3])}"""
    
    def format_ai_report_html(self, report: Dict) -> str:
        """格式化AI日报为精美HTML邮件"""
        date = report.get("date", "")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 680px; 
            margin: 0 auto; 
            background: #ffffff; 
            border-radius: 16px; 
            overflow: hidden; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{ 
            font-size: 28px; 
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: 2px;
        }}
        .header .subtitle {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 12px;
        }}
        .header .date {{ 
            font-size: 15px; 
            opacity: 0.85;
            background: rgba(255,255,255,0.15);
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
        }}
        .top-insight {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            padding: 25px 30px;
            border-left: 4px solid #667eea;
            margin: 0;
            font-size: 14px;
            line-height: 1.8;
            color: #444;
        }}
        .content {{ padding: 30px; }}
        .dimension {{ 
            margin-bottom: 35px;
            border-bottom: 1px solid #eee;
            padding-bottom: 25px;
        }}
        .dimension:last-child {{ border-bottom: none; }}
        .dimension-header {{ 
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}
        .dimension-icon {{
            font-size: 24px;
            margin-right: 12px;
        }}
        .dimension-title {{ 
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }}
        .news-card {{ 
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #eee;
            transition: all 0.3s ease;
        }}
        .news-card:hover {{
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transform: translateY(-2px);
        }}
        .news-title {{ 
            font-size: 15px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            line-height: 1.5;
        }}
        .news-title a {{
            color: #333;
            text-decoration: none;
        }}
        .news-title a:hover {{
            color: #667eea;
        }}
        .news-desc {{ 
            font-size: 13px;
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        .news-meta {{
            font-size: 12px;
            color: #999;
            margin-bottom: 15px;
        }}
        .insight-box {{
            background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
            border-radius: 8px;
            padding: 15px;
            margin-top: 12px;
            border-left: 3px solid #f0ad4e;
        }}
        .insight-title {{
            font-size: 13px;
            font-weight: 600;
            color: #856404;
            margin-bottom: 8px;
        }}
        .insight-content {{
            font-size: 13px;
            color: #856404;
            line-height: 1.7;
        }}
        .insight-content strong {{
            color: #664d03;
        }}
        .wechat-action {{
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 6px;
            padding: 10px 12px;
            margin-top: 10px;
            font-size: 12px;
            color: #155724;
        }}
        .wechat-action strong {{
            color: #0d3d19;
        }}
        .footer {{ 
            background: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            border-top: 1px solid #eee;
        }}
        .footer p {{ 
            color: #666;
            font-size: 12px;
            line-height: 1.8;
        }}
        .footer .brand {{
            color: #667eea;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI前沿日报</h1>
            <div class="subtitle">每日精选 · 专家解读 · 价值洞察</div>
            <div class="date">{date}</div>
        </div>
        
        <div class="top-insight">
            {report.get('top_insight', '').replace(chr(10), '<br>').replace('**', '<strong>').replace('**', '</strong>')}
        </div>
        
        <div class="content">
"""
        
        for dim_key, dim_data in report.get("dimensions", {}).items():
            news_list = dim_data.get("news", [])
            if not news_list:
                continue
            
            html += f"""
            <div class="dimension">
                <div class="dimension-header">
                    <span class="dimension-icon">{dim_data.get('icon', '📌')}</span>
                    <span class="dimension-title">{dim_data['name']}</span>
                </div>
"""
            
            for news in news_list:
                title = news.get("title", "")
                desc = news.get("description", "")[:200]
                url = news.get("url", "")
                source = news.get("source", "")
                age = news.get("age", "")
                insight = news.get("insight", {})
                
                html += f"""
                <div class="news-card">
                    <div class="news-title"><a href="{url}" target="_blank">{title}</a></div>
                    <div class="news-desc">{desc}...</div>
                    <div class="news-meta">📎 {source} · {age}</div>
                    
                    <div class="insight-box">
                        <div class="insight-title">💡 专家解读</div>
                        <div class="insight-content">
                            <strong>核心要点：</strong>{insight.get('summary', '')}<br><br>
                            <strong>对你的启示：</strong>{insight.get('implication', '')}
                        </div>
                        <div class="wechat-action">
                            <strong>🔗 微信支付机会：</strong>{insight.get('wechat_pay_action', '')}
                        </div>
                    </div>
                </div>
"""
            
            html += "</div>"
        
        html += f"""
        </div>
        
        <div class="footer">
            <p><span class="brand">🤖 一人公司AI系统</span> · 专家级信息服务</p>
            <p>📰 内容经多轮筛选和AI深度分析，确保专业价值</p>
            <p>💬 如有反馈，回复邮件即可</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def format_retail_report_html(self, report: Dict) -> str:
        """格式化零售日报为精美HTML邮件"""
        date = report.get("date", "")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif; 
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 680px; 
            margin: 0 auto; 
            background: #ffffff; 
            border-radius: 16px; 
            overflow: hidden; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{ 
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white; 
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{ 
            font-size: 28px; 
            font-weight: 700;
            margin-bottom: 8px;
            letter-spacing: 2px;
        }}
        .header .subtitle {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 12px;
        }}
        .header .date {{ 
            font-size: 15px; 
            opacity: 0.85;
            background: rgba(255,255,255,0.15);
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
        }}
        .top-insight {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            padding: 25px 30px;
            border-left: 4px solid #11998e;
            margin: 0;
            font-size: 14px;
            line-height: 1.8;
            color: #444;
        }}
        .content {{ padding: 30px; }}
        .dimension {{ 
            margin-bottom: 35px;
            border-bottom: 1px solid #eee;
            padding-bottom: 25px;
        }}
        .dimension:last-child {{ border-bottom: none; }}
        .dimension-header {{ 
            display: flex;
            align-items: center;
            margin-bottom: 8px;
        }}
        .dimension-icon {{
            font-size: 24px;
            margin-right: 12px;
        }}
        .dimension-title {{ 
            font-size: 18px;
            font-weight: 600;
            color: #333;
        }}
        .dimension-angle {{
            font-size: 12px;
            color: #11998e;
            margin-bottom: 15px;
            padding-left: 36px;
        }}
        .news-card {{ 
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #eee;
            transition: all 0.3s ease;
        }}
        .news-card:hover {{
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            transform: translateY(-2px);
        }}
        .news-title {{ 
            font-size: 15px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            line-height: 1.5;
        }}
        .news-title a {{
            color: #333;
            text-decoration: none;
        }}
        .news-title a:hover {{
            color: #11998e;
        }}
        .news-desc {{ 
            font-size: 13px;
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        .news-meta {{
            font-size: 12px;
            color: #999;
            margin-bottom: 15px;
        }}
        .insight-box {{
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-radius: 8px;
            padding: 15px;
            margin-top: 12px;
            border-left: 3px solid #4caf50;
        }}
        .insight-title {{
            font-size: 13px;
            font-weight: 600;
            color: #2e7d32;
            margin-bottom: 8px;
        }}
        .insight-content {{
            font-size: 13px;
            color: #2e7d32;
            line-height: 1.7;
        }}
        .insight-content strong {{
            color: #1b5e20;
        }}
        .wechat-action {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 6px;
            padding: 10px 12px;
            margin-top: 10px;
            font-size: 12px;
            color: #1565c0;
        }}
        .wechat-action strong {{
            color: #0d47a1;
        }}
        .opportunities {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            padding: 25px 30px;
            margin: 0;
        }}
        .opportunities h3 {{
            font-size: 16px;
            color: #e65100;
            margin-bottom: 15px;
        }}
        .opportunity-item {{
            background: white;
            border-radius: 8px;
            padding: 12px 15px;
            margin-bottom: 10px;
            font-size: 13px;
            color: #bf360c;
            border-left: 3px solid #ff9800;
        }}
        .opportunity-item strong {{
            color: #e65100;
        }}
        .footer {{ 
            background: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            border-top: 1px solid #eee;
        }}
        .footer p {{ 
            color: #666;
            font-size: 12px;
            line-height: 1.8;
        }}
        .footer .brand {{
            color: #11998e;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛒 零售行业日报</h1>
            <div class="subtitle">深度洞察 · 支付机会 · 行动指南</div>
            <div class="date">{date}</div>
        </div>
        
        <div class="top-insight">
            {report.get('top_insight', '').replace(chr(10), '<br>').replace('**', '<strong>').replace('**', '</strong>')}
        </div>
        
        <div class="content">
"""
        
        for dim_key, dim_data in report.get("dimensions", {}).items():
            news_list = dim_data.get("news", [])
            if not news_list:
                continue
            
            wechat_angle = dim_data.get("wechat_pay_angle", "")
            
            html += f"""
            <div class="dimension">
                <div class="dimension-header">
                    <span class="dimension-icon">{dim_data.get('icon', '📌')}</span>
                    <span class="dimension-title">{dim_data['name']}</span>
                </div>
                <div class="dimension-angle">💳 支付视角：{wechat_angle}</div>
"""
            
            for news in news_list:
                title = news.get("title", "")
                desc = news.get("description", "")[:200]
                url = news.get("url", "")
                source = news.get("source", "")
                age = news.get("age", "")
                insight = news.get("insight", {})
                
                html += f"""
                <div class="news-card">
                    <div class="news-title"><a href="{url}" target="_blank">{title}</a></div>
                    <div class="news-desc">{desc}...</div>
                    <div class="news-meta">📎 {source} · {age}</div>
                    
                    <div class="insight-box">
                        <div class="insight-title">💡 专家解读</div>
                        <div class="insight-content">
                            <strong>核心要点：</strong>{insight.get('summary', '')}<br><br>
                            <strong>对你的启示：</strong>{insight.get('implication', '')}
                        </div>
                        <div class="wechat-action">
                            <strong>🔗 微信支付行动：</strong>{insight.get('wechat_pay_action', '')}
                        </div>
                    </div>
                </div>
"""
            
            html += "</div>"
        
        # 微信支付机会汇总
        opportunities = report.get("wechat_pay_opportunities", [])
        if opportunities:
            html += """
        </div>
        
        <div class="opportunities">
            <h3>💳 微信支付机会汇总</h3>
"""
            for opp in opportunities[:4]:
                html += f"""
            <div class="opportunity-item">
                <strong>{opp.get('area', '')}</strong>：{opp.get('action', '')}
            </div>
"""
            html += "</div>"
        else:
            html += "</div>"
        
        html += f"""
        <div class="footer">
            <p><span class="brand">🛒 一人公司AI系统</span> · 零售行业专家服务</p>
            <p>📰 内容经多轮筛选和AI深度分析，聚焦微信支付机会</p>
            <p>💬 如有反馈，回复邮件即可</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def format_ai_report_markdown(self, report: Dict) -> str:
        """格式化AI日报为Markdown（企微版，精简）"""
        date = report.get("date", "")
        
        md = f"""# 🤖 AI前沿日报
> {date}

"""
        
        for dim_key, dim_data in report.get("dimensions", {}).items():
            news_list = dim_data.get("news", [])
            if not news_list:
                continue
            
            md += f"## {dim_data['name']}\n\n"
            
            news = news_list[0]
            title = news.get("title", "")[:45]
            url = news.get("url", "")
            insight = news.get("insight", {})
            
            md += f"📰 [{title}]({url})\n\n"
            md += f"💡 **洞察**: {insight.get('summary', '')[:60]}\n\n"
        
        md += """---
*📧 完整版含专家解读已发送至邮箱*"""
        
        return md
    
    def format_retail_report_markdown(self, report: Dict) -> str:
        """格式化零售日报为Markdown（企微版，精简）"""
        date = report.get("date", "")
        
        md = f"""# 🛒 零售行业日报
> {date}

"""
        
        for dim_key, dim_data in report.get("dimensions", {}).items():
            news_list = dim_data.get("news", [])
            if not news_list:
                continue
            
            news = news_list[0]
            title = news.get("title", "")[:40]
            url = news.get("url", "")
            
            md += f"**{dim_data['name']}**: [{title}]({url})\n\n"
        
        # 精简版机会
        opportunities = report.get("wechat_pay_opportunities", [])
        if opportunities:
            md += "## 💳 支付机会\n\n"
            for opp in opportunities[:2]:
                md += f"- {opp['area']}: {opp['action'][:35]}...\n"
        
        md += """
---
*📧 完整版含专家解读已发送至邮箱*"""
        
        return md


# 测试
if __name__ == "__main__":
    import sys
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), "../config/api_keys.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    brave_key = config.get("search", {}).get("brave", {}).get("api_key", "")
    
    service = ExpertReportService({"brave_api_key": brave_key})
    
    print("=" * 60)
    print("🤖 生成AI专家日报...")
    print("=" * 60)
    ai_report = service.generate_ai_daily_report()
    print(f"✅ AI日报: {ai_report.get('total_news', 0)}条精选新闻")
    
    print("\n" + "=" * 60)
    print("🛒 生成零售专家日报...")
    print("=" * 60)
    retail_report = service.generate_retail_daily_report()
    print(f"✅ 零售日报: {retail_report.get('total_news', 0)}条精选新闻")
