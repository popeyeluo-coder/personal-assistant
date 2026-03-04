"""
专业日报服务
- AI前沿日报：硬件、模型、算法、应用
- 零售行业日报：国内外市场、各赛道分析、微信支付机会
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yaml

logger = logging.getLogger(__name__)

# Brave Search API
BRAVE_API_URL = "https://api.search.brave.com/res/v1/news/search"


class ProfessionalReportService:
    """
    专业日报生成服务
    作为用户的唯一信息源，确保内容质量
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.brave_api_key = self.config.get("brave_api_key", "")
        
        # AI日报框架
        self.ai_dimensions = {
            "hardware": {
                "name": "🔧 硬件/芯片",
                "keywords": ["AI芯片", "GPU", "NPU", "NVIDIA", "TPU", "算力", "AI服务器", "边缘计算芯片"],
                "en_keywords": ["AI chip", "NVIDIA GPU", "TPU", "AI accelerator", "neural processor"]
            },
            "models": {
                "name": "🧠 大模型/基础模型", 
                "keywords": ["大模型", "GPT", "Claude", "Gemini", "通义千问", "文心一言", "DeepSeek", "开源模型", "多模态模型"],
                "en_keywords": ["LLM", "GPT-5", "Claude", "Gemini", "open source AI model", "multimodal AI"]
            },
            "algorithms": {
                "name": "⚙️ 算法/技术",
                "keywords": ["AI算法", "机器学习", "强化学习", "RAG", "Agent", "微调", "推理优化", "训练方法"],
                "en_keywords": ["AI algorithm", "machine learning", "reinforcement learning", "fine-tuning", "AI agent"]
            },
            "applications": {
                "name": "📱 应用/产品",
                "keywords": ["AI应用", "AI产品", "AIGC", "AI助手", "AI编程", "AI绘画", "AI视频", "AI办公"],
                "en_keywords": ["AI application", "AI product", "AIGC", "AI assistant", "AI coding", "AI video"]
            },
            "industry": {
                "name": "🏢 产业/投资",
                "keywords": ["AI投资", "AI融资", "AI公司", "AI政策", "AI监管", "AI人才"],
                "en_keywords": ["AI investment", "AI funding", "AI startup", "AI regulation", "AI policy"]
            }
        }
        
        # 零售日报框架
        self.retail_dimensions = {
            "convenience": {
                "name": "🏪 便利店",
                "keywords": ["便利店", "7-11", "全家", "罗森", "便利蜂", "美宜佳"],
                "en_keywords": ["convenience store", "7-Eleven", "FamilyMart", "Lawson"]
            },
            "supermarket": {
                "name": "🛒 商超",
                "keywords": ["超市", "沃尔玛", "家乐福", "盒马", "山姆", "Costco", "永辉"],
                "en_keywords": ["supermarket", "Walmart", "Costco", "Sam's Club", "grocery retail"]
            },
            "mall": {
                "name": "🏬 商圈/购物中心",
                "keywords": ["购物中心", "商圈", "万达", "太古里", "SKP", "商场客流"],
                "en_keywords": ["shopping mall", "retail district", "shopping center"]
            },
            "dutyfree": {
                "name": "✈️ 免税",
                "keywords": ["免税店", "中免", "海南免税", "机场免税", "离岛免税"],
                "en_keywords": ["duty free", "travel retail", "airport retail"]
            },
            "discount": {
                "name": "🍬 零食折扣",
                "keywords": ["零食折扣", "零食很忙", "赵一鸣", "好特卖", "折扣零售", "硬折扣"],
                "en_keywords": ["discount retail", "snack discount", "hard discount"]
            },
            "payment": {
                "name": "💳 支付/金融科技",
                "keywords": ["移动支付", "微信支付", "支付宝", "数字人民币", "刷脸支付"],
                "en_keywords": ["mobile payment", "digital payment", "fintech retail"]
            }
        }
    
    def search_news(self, query: str, count: int = 10, freshness: str = "pd") -> List[Dict]:
        """
        使用Brave Search搜索新闻
        
        Args:
            query: 搜索关键词
            count: 返回数量
            freshness: 时效性 (pd=过去24小时, pw=过去一周)
        """
        if not self.brave_api_key:
            logger.warning("未配置Brave API Key")
            return []
        
        try:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": self.brave_api_key
            }
            
            params = {
                "q": query,
                "count": count,
                "freshness": freshness,
                "text_decorations": False,
                "spellcheck": False
            }
            
            response = requests.get(
                BRAVE_API_URL,
                headers=headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                
                # 提取关键信息
                news_list = []
                for item in results:
                    news_list.append({
                        "title": item.get("title", ""),
                        "description": item.get("description", ""),
                        "url": item.get("url", ""),
                        "source": item.get("meta_url", {}).get("hostname", ""),
                        "age": item.get("age", ""),
                        "thumbnail": item.get("thumbnail", {}).get("src", "")
                    })
                
                return news_list
            else:
                logger.error(f"Brave搜索失败: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"搜索异常: {e}")
            return []
    
    def search_web(self, query: str, count: int = 10) -> List[Dict]:
        """使用Brave Web Search搜索"""
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
                "freshness": "pd"  # 过去24小时
            }
            
            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=15
            )
            
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
    
    def filter_valuable_news(self, news_list: List[Dict], min_desc_len: int = 50) -> List[Dict]:
        """
        过滤有价值的新闻
        - 去除描述过短的
        - 去除重复的
        - 去除低质量来源
        """
        seen_titles = set()
        filtered = []
        
        # 低质量来源黑名单
        blacklist_sources = ["pinterest", "facebook", "instagram", "tiktok"]
        
        for news in news_list:
            title = news.get("title", "")
            desc = news.get("description", "")
            source = news.get("source", "").lower()
            url = news.get("url", "")
            
            # 过滤条件
            if not title or not url:
                continue
            if len(desc) < min_desc_len:
                continue
            if any(b in source for b in blacklist_sources):
                continue
            if title in seen_titles:
                continue
            
            seen_titles.add(title)
            filtered.append(news)
        
        return filtered
    
    def generate_ai_report(self) -> Dict:
        """
        生成AI前沿日报
        """
        report_date = datetime.now().strftime("%Y年%m月%d日")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%m月%d日")
        
        report = {
            "title": f"🤖 AI前沿日报",
            "date": report_date,
            "dimensions": {},
            "summary": "",
            "insights": []
        }
        
        all_news = []
        
        # 按维度搜索新闻
        for dim_key, dim_info in self.ai_dimensions.items():
            dim_news = []
            
            # 中文搜索
            for keyword in dim_info["keywords"][:3]:
                results = self.search_news(f"{keyword} 最新", count=5)
                dim_news.extend(results)
            
            # 英文搜索（获取国际视野）
            for keyword in dim_info["en_keywords"][:2]:
                results = self.search_news(f"{keyword} news", count=3)
                dim_news.extend(results)
            
            # 过滤和去重
            filtered_news = self.filter_valuable_news(dim_news)[:5]
            
            report["dimensions"][dim_key] = {
                "name": dim_info["name"],
                "news": filtered_news,
                "count": len(filtered_news)
            }
            
            all_news.extend(filtered_news)
        
        # 生成总结
        report["summary"] = self._generate_ai_summary(report["dimensions"])
        report["total_news"] = len(all_news)
        
        return report
    
    def generate_retail_report(self) -> Dict:
        """
        生成零售行业日报
        """
        report_date = datetime.now().strftime("%Y年%m月%d日")
        
        report = {
            "title": f"🛒 零售行业日报",
            "date": report_date,
            "domestic": {},  # 国内市场
            "overseas": {},  # 海外市场
            "wechat_pay_opportunities": [],  # 微信支付机会
            "summary": ""
        }
        
        # 国内市场搜索
        for dim_key, dim_info in self.retail_dimensions.items():
            dim_news = []
            
            for keyword in dim_info["keywords"][:3]:
                results = self.search_news(f"{keyword} 最新动态", count=5)
                dim_news.extend(results)
            
            filtered_news = self.filter_valuable_news(dim_news)[:4]
            
            report["domestic"][dim_key] = {
                "name": dim_info["name"],
                "news": filtered_news,
                "count": len(filtered_news)
            }
        
        # 海外市场搜索
        overseas_keywords = [
            ("convenience store news", "便利店"),
            ("Walmart retail news", "沃尔玛"),
            ("retail industry news", "零售业"),
            ("e-commerce retail", "电商零售"),
            ("discount retail Europe", "折扣零售")
        ]
        
        overseas_news = []
        for en_kw, cn_label in overseas_keywords:
            results = self.search_news(en_kw, count=3)
            for r in results:
                r["category"] = cn_label
            overseas_news.extend(results)
        
        report["overseas"]["news"] = self.filter_valuable_news(overseas_news)[:8]
        
        # 生成微信支付机会洞察
        report["wechat_pay_opportunities"] = self._analyze_wechat_pay_opportunities(report)
        
        # 生成总结
        report["summary"] = self._generate_retail_summary(report)
        
        return report
    
    def _generate_ai_summary(self, dimensions: Dict) -> str:
        """生成AI日报总结"""
        summaries = []
        
        for dim_key, dim_data in dimensions.items():
            news_count = dim_data.get("count", 0)
            if news_count > 0:
                # 提取关键标题作为摘要线索
                titles = [n.get("title", "")[:30] for n in dim_data.get("news", [])[:2]]
                if titles:
                    summaries.append(f"**{dim_data['name']}**: 今日{news_count}条相关动态")
        
        if summaries:
            return "📊 **今日AI领域动态概览**\n" + "\n".join(summaries)
        return "今日AI领域暂无重大更新"
    
    def _generate_retail_summary(self, report: Dict) -> str:
        """生成零售日报总结"""
        domestic_count = sum(d.get("count", 0) for d in report.get("domestic", {}).values())
        overseas_count = len(report.get("overseas", {}).get("news", []))
        
        return f"""📊 **今日零售行业动态**
- 国内市场: {domestic_count}条要闻
- 海外市场: {overseas_count}条要闻
- 微信支付机会: {len(report.get('wechat_pay_opportunities', []))}个洞察"""
    
    def _analyze_wechat_pay_opportunities(self, report: Dict) -> List[Dict]:
        """
        分析微信支付可以参与的机会
        基于新闻内容提取商业洞察
        """
        opportunities = []
        
        # 便利店机会
        convenience_news = report.get("domestic", {}).get("convenience", {}).get("news", [])
        if convenience_news:
            opportunities.append({
                "area": "🏪 便利店",
                "insight": "便利店数字化转型持续，微信支付可深化会员体系、小程序点单、无人货架等场景合作",
                "action": "拓展便利店品牌合作，推广刷脸支付设备"
            })
        
        # 商超机会
        supermarket_news = report.get("domestic", {}).get("supermarket", {}).get("news", [])
        if supermarket_news:
            opportunities.append({
                "area": "🛒 商超",
                "insight": "商超自助结账、到家业务增长，支付+小程序+企微私域三位一体方案有需求",
                "action": "推广商超小程序解决方案，强化到家业务支付体验"
            })
        
        # 免税机会
        dutyfree_news = report.get("domestic", {}).get("dutyfree", {}).get("news", [])
        if dutyfree_news:
            opportunities.append({
                "area": "✈️ 免税",
                "insight": "入境游恢复带动免税消费，境外游客支付便利化是重点",
                "action": "推广外卡支付、境外钱包互通方案"
            })
        
        # 折扣零售机会
        discount_news = report.get("domestic", {}).get("discount", {}).get("news", [])
        if discount_news:
            opportunities.append({
                "area": "🍬 折扣零售",
                "insight": "硬折扣赛道高速扩张，新品牌门店快速铺开需要支付解决方案",
                "action": "主动对接零食折扣品牌，提供门店快速接入方案"
            })
        
        return opportunities
    
    def format_ai_report_markdown(self, report: Dict) -> str:
        """格式化AI日报为Markdown（企微版，限制长度）"""
        date = report.get("date", "")
        
        md = f"""# 🤖 AI前沿日报
> {date}

"""
        
        # 只展示每个维度最重要的1条新闻，确保不超过4096字符
        for dim_key, dim_data in report.get("dimensions", {}).items():
            news_list = dim_data.get("news", [])
            if not news_list:
                continue
            
            md += f"## {dim_data['name']}\n"
            
            # 只取第一条最重要的
            news = news_list[0]
            title = news.get("title", "")[:40]
            url = news.get("url", "")
            
            md += f"[{title}]({url})\n\n"
        
        md += """---
*📧 完整版已发送至邮箱*"""
        
        return md
    
    def format_retail_report_markdown(self, report: Dict) -> str:
        """格式化零售日报为Markdown（企微版，限制长度）"""
        date = report.get("date", "")
        
        md = f"""# 🛒 零售行业日报
> {date}

## 🇨🇳 国内市场
"""
        
        # 每个赛道只展示1条
        for dim_key, dim_data in report.get("domestic", {}).items():
            news_list = dim_data.get("news", [])
            if not news_list:
                continue
            
            news = news_list[0]
            title = news.get("title", "")[:35]
            url = news.get("url", "")
            
            md += f"**{dim_data['name']}**: [{title}]({url})\n"
        
        # 微信支付机会（精简版）
        opportunities = report.get("wechat_pay_opportunities", [])
        if opportunities:
            md += "\n## 💳 微信支付机会\n"
            for opp in opportunities[:2]:
                md += f"- {opp['area']}: {opp['action'][:30]}\n"
        
        md += """
---
*📧 完整版已发送至邮箱*"""
        
        return md
    
    def format_ai_report_html(self, report: Dict) -> str:
        """格式化AI日报为HTML（邮件版）"""
        date = report.get("date", "")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 700px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                .content {{ padding: 25px; }}
                .summary {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #667eea; }}
                .dimension {{ margin-bottom: 25px; }}
                .dimension h3 {{ color: #333; border-bottom: 2px solid #eee; padding-bottom: 8px; }}
                .news-item {{ margin: 15px 0; padding: 15px; background: #fafafa; border-radius: 8px; }}
                .news-item h4 {{ margin: 0 0 8px 0; color: #333; font-size: 15px; }}
                .news-item p {{ margin: 0 0 8px 0; color: #666; font-size: 14px; line-height: 1.5; }}
                .news-item a {{ color: #667eea; text-decoration: none; font-size: 13px; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 AI前沿日报</h1>
                    <p>{date}</p>
                </div>
                <div class="content">
                    <div class="summary">{report.get('summary', '').replace(chr(10), '<br>')}</div>
        """
        
        for dim_key, dim_data in report.get("dimensions", {}).items():
            news_list = dim_data.get("news", [])
            if not news_list:
                continue
            
            html += f'<div class="dimension"><h3>{dim_data["name"]}</h3>'
            
            for news in news_list[:3]:
                title = news.get("title", "")
                desc = news.get("description", "")
                url = news.get("url", "")
                source = news.get("source", "")
                
                html += f'''
                <div class="news-item">
                    <h4>{title}</h4>
                    <p>{desc}</p>
                    <a href="{url}" target="_blank">📎 {source} - 查看原文</a>
                </div>
                '''
            
            html += '</div>'
        
        html += """
                </div>
                <div class="footer">
                    <p>🤖 一人公司AI系统 · 每日8:00自动推送</p>
                    <p>💡 内容已经过筛选审核，确保信息价值</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def format_retail_report_html(self, report: Dict) -> str:
        """格式化零售日报为HTML（邮件版）"""
        date = report.get("date", "")
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 700px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 30px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .section {{ padding: 20px 25px; border-bottom: 1px solid #eee; }}
                .section h2 {{ color: #333; margin-top: 0; }}
                .section h3 {{ color: #555; font-size: 16px; }}
                .news-item {{ margin: 12px 0; padding: 12px; background: #f8f9fa; border-radius: 6px; }}
                .news-item h4 {{ margin: 0 0 6px 0; font-size: 14px; }}
                .news-item p {{ margin: 0 0 6px 0; color: #666; font-size: 13px; }}
                .news-item a {{ color: #11998e; text-decoration: none; font-size: 12px; }}
                .opportunity {{ background: #fff3cd; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                .opportunity h4 {{ margin: 0 0 8px 0; color: #856404; }}
                .opportunity p {{ margin: 4px 0; font-size: 13px; color: #856404; }}
                .footer {{ padding: 20px; text-align: center; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛒 零售行业日报</h1>
                    <p>{date}</p>
                </div>
                
                <div class="section">
                    <h2>🇨🇳 国内市场</h2>
        """
        
        for dim_key, dim_data in report.get("domestic", {}).items():
            news_list = dim_data.get("news", [])
            if not news_list:
                continue
            
            html += f'<h3>{dim_data["name"]}</h3>'
            
            for news in news_list[:2]:
                title = news.get("title", "")
                desc = news.get("description", "")[:100]
                url = news.get("url", "")
                
                html += f'''
                <div class="news-item">
                    <h4>{title}</h4>
                    <p>{desc}...</p>
                    <a href="{url}" target="_blank">🔗 查看详情</a>
                </div>
                '''
        
        html += '</div><div class="section"><h2>🌍 海外市场</h2>'
        
        overseas_news = report.get("overseas", {}).get("news", [])
        for news in overseas_news[:4]:
            title = news.get("title", "")
            url = news.get("url", "")
            html += f'<div class="news-item"><a href="{url}" target="_blank">{title}</a></div>'
        
        html += '</div><div class="section"><h2>💳 微信支付机会洞察</h2>'
        
        opportunities = report.get("wechat_pay_opportunities", [])
        for opp in opportunities:
            html += f'''
            <div class="opportunity">
                <h4>{opp['area']}</h4>
                <p><strong>洞察:</strong> {opp['insight']}</p>
                <p><strong>建议:</strong> {opp['action']}</p>
            </div>
            '''
        
        html += """
                </div>
                <div class="footer">
                    <p>🤖 一人公司AI系统 · 每日8:00自动推送</p>
                    <p>💡 作为您的唯一信息源，内容已严格筛选</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# 测试
if __name__ == "__main__":
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), "../config/api_keys.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    brave_key = config.get("search", {}).get("brave", {}).get("api_key", "")
    
    service = ProfessionalReportService({"brave_api_key": brave_key})
    
    print("生成AI日报...")
    ai_report = service.generate_ai_report()
    print(f"AI日报: {ai_report.get('total_news', 0)}条新闻")
    
    print("\n生成零售日报...")
    retail_report = service.generate_retail_report()
    print(f"零售日报: 国内{sum(d.get('count', 0) for d in retail_report.get('domestic', {}).values())}条")
