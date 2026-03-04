# -*- coding: utf-8 -*-
"""
AI日报系统 - 报告生成模块（增强版）
按产业链分类展示，包含三层专业点评
"""
import sys
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from jinja2 import Template

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import STORAGE_CONFIG


class AIReportGenerator:
    """AI日报报告生成器"""
    
    def __init__(self):
        self.report_dir = Path(__file__).parent.parent / STORAGE_CONFIG["report_dir"]
        self.report_dir.mkdir(exist_ok=True)
    
    def generate_html_report(self, analysis_results: Dict) -> str:
        template = Template(self._get_report_template())
        
        items = analysis_results.get("items", [])
        chain_groups = analysis_results.get("chain_groups", {})
        overall_review = analysis_results.get("overall_review", {})
        chain_reviews = analysis_results.get("chain_reviews", {})
        summary = analysis_results.get("summary", {})
        
        p1_items = [item for item in items if item.get("priority") == "P1"]
        p2_items = [item for item in items if item.get("priority") == "P2"]
        
        today = datetime.now()
        context = {
            "report_date": today.strftime("%Y年%m月%d日"),
            "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][today.weekday()],
            "total_items": len(items),
            "overall_review": overall_review,
            "chain_reviews": chain_reviews,
            "chain_groups": chain_groups,
            "p1_items": p1_items[:12],
            "p2_items": p2_items[:10],
            "summary": summary,
            "hot_companies": summary.get("hot_companies", [])[:10],
            "new_count": summary.get("new_count", 0),
            "priority_counts": summary.get("priority_counts", {}),
            "expert_overview": overall_review,  # 兼容
        }
        
        html_content = template.render(**context)
        self._save_report(html_content, today)
        return html_content
    
    def _save_report(self, html_content: str, date: datetime):
        filename = f"ai_daily_{date.strftime('%Y%m%d')}.html"
        filepath = self.report_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"   ✓ 报告已保存: {filepath}")
    
    def _get_report_template(self) -> str:
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI日报 - {{ report_date }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; padding: 30px; border-radius: 16px; margin-bottom: 20px; text-align: center;
        }
        .header h1 { font-size: 28px; margin-bottom: 8px; }
        .header .date { font-size: 16px; opacity: 0.9; }
        .header .stats { display: flex; justify-content: center; gap: 40px; margin-top: 15px; }
        .header .stat-item { text-align: center; }
        .header .stat-value { font-size: 28px; font-weight: bold; }
        .header .stat-label { font-size: 12px; opacity: 0.8; }
        
        /* 整体点评卡片 */
        .overview-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border-radius: 16px; padding: 24px; margin-bottom: 20px; color: white;
        }
        .overview-card .title { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: bold; margin-bottom: 15px; }
        .overview-card .risk-badge { font-size: 12px; padding: 4px 12px; border-radius: 12px; background: rgba(255,255,255,0.2); }
        .overview-card .overview-text { font-size: 15px; line-height: 1.8; margin-bottom: 20px; }
        
        .review-section { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .review-box { background: rgba(255,255,255,0.15); border-radius: 10px; padding: 15px; }
        .review-box .box-title { font-size: 13px; font-weight: bold; margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
        .review-box .box-item { font-size: 12px; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .review-box .box-item:last-child { border-bottom: none; }
        
        /* 产业链卡片 */
        .chain-section { background: white; border-radius: 12px; padding: 20px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .chain-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; padding-bottom: 12px; border-bottom: 2px solid #f0f0f0; }
        .chain-header .left { display: flex; align-items: center; gap: 10px; }
        .chain-header .icon { font-size: 24px; }
        .chain-header h2 { font-size: 18px; color: #333; }
        .chain-header .count { background: #667eea; color: white; font-size: 12px; padding: 3px 10px; border-radius: 10px; }
        .chain-header .p1-badge { background: #dc3545; color: white; font-size: 11px; padding: 2px 8px; border-radius: 8px; margin-left: 8px; }
        
        .chain-review { background: #f8f9fa; border-radius: 10px; padding: 15px; margin-bottom: 15px; }
        .chain-review .summary { font-size: 14px; color: #333; margin-bottom: 12px; font-weight: 500; }
        .chain-review .focus-list { display: flex; flex-wrap: wrap; gap: 8px; }
        .chain-review .focus-item { font-size: 12px; background: #e3f2fd; color: #1976d2; padding: 4px 10px; border-radius: 6px; }
        .chain-review .reason-item { font-size: 12px; background: #fff3e0; color: #e65100; padding: 4px 10px; border-radius: 6px; }
        
        /* 新闻卡片 */
        .news-item { padding: 15px; border-radius: 10px; margin-bottom: 12px; background: #f8f9fa; border-left: 4px solid #667eea; transition: all 0.2s; position: relative; }
        .news-item:hover { transform: translateX(3px); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
        .news-item.p1 { border-left-color: #dc3545; background: #fff5f5; }
        .news-item.p2 { border-left-color: #fd7e14; background: #fff8f0; }
        .news-item.new::after { content: "新"; position: absolute; top: -5px; right: 10px; background: #dc3545; color: white; font-size: 10px; padding: 2px 6px; border-radius: 8px; }
        
        .news-title { font-size: 15px; font-weight: 600; margin-bottom: 8px; }
        .news-title a { color: #333; text-decoration: none; }
        .news-title a:hover { color: #667eea; }
        
        .news-meta { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; }
        .meta-tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; }
        .meta-tag.priority { background: #dc3545; color: white; }
        .meta-tag.priority.p2 { background: #fd7e14; }
        .meta-tag.chain { background: #667eea; color: white; }
        .meta-tag.event { background: #6c757d; color: white; }
        .meta-tag.company { background: #28a745; color: white; }
        
        .news-comment { font-size: 13px; color: #444; padding: 10px 12px; background: white; border-radius: 8px; margin-top: 10px; }
        .news-comment .focus { color: #1976d2; font-weight: 500; }
        .news-comment .reason { color: #666; font-size: 12px; margin-top: 5px; }
        
        .news-summary { font-size: 13px; color: #666; margin-top: 8px; }
        
        .hot-companies { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 15px; }
        .company-tag { background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 6px 14px; border-radius: 15px; font-size: 12px; }
        
        .footer { text-align: center; padding: 25px; color: #999; font-size: 12px; }
        
        @media (max-width: 600px) {
            .review-section { grid-template-columns: 1fr; }
            .header .stats { gap: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>🤖 AI日报</h1>
            <div class="date">{{ report_date }} {{ weekday }}</div>
            <div class="stats">
                <div class="stat-item"><div class="stat-value">{{ total_items }}</div><div class="stat-label">今日新闻</div></div>
                <div class="stat-item"><div class="stat-value">{{ priority_counts.get('P1', 0) }}</div><div class="stat-label">高优</div></div>
                <div class="stat-item"><div class="stat-value">{{ priority_counts.get('P2', 0) }}</div><div class="stat-label">重要</div></div>
                <div class="stat-item"><div class="stat-value">{{ new_count }}</div><div class="stat-label">新信息</div></div>
            </div>
        </div>
        
        <!-- 整体点评 -->
        {% if overall_review %}
        <div class="overview-card">
            <div class="title">
                <span>📊 今日整体点评</span>
                <span class="risk-badge" style="background: {{ overall_review.risk_color }};">{{ overall_review.risk_level }}关注度</span>
            </div>
            <div class="overview-text">{{ overall_review.overview }}</div>
            
            <div class="review-section">
                {% if overall_review.focus_points %}
                <div class="review-box">
                    <div class="box-title">🎯 您需要关注</div>
                    {% for point in overall_review.focus_points %}
                    <div class="box-item">{{ point }}</div>
                    {% endfor %}
                </div>
                {% endif %}
                
                {% if overall_review.reasons %}
                <div class="review-box">
                    <div class="box-title">💡 原因分析</div>
                    {% for reason in overall_review.reasons %}
                    <div class="box-item">{{ reason }}</div>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            
            {% if overall_review.recommendations %}
            <div class="review-box" style="margin-top: 15px;">
                <div class="box-title">✅ 今日建议</div>
                {% for rec in overall_review.recommendations %}
                <div class="box-item">→ {{ rec }}</div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <!-- 按产业链展示 -->
        {% for chain_key, review in chain_reviews.items() %}
        {% if review.total > 0 %}
        <div class="chain-section">
            <div class="chain-header">
                <div class="left">
                    <span class="icon">{{ review.icon }}</span>
                    <h2>{{ review.name }}</h2>
                    <span class="count">{{ review.total }}条</span>
                    {% if review.p1_count > 0 %}<span class="p1-badge">{{ review.p1_count }}条高优</span>{% endif %}
                </div>
            </div>
            
            <!-- 产业链点评 -->
            <div class="chain-review">
                <div class="summary">{{ review.summary }}</div>
                <div class="focus-list">
                    {% for point in review.focus_points %}
                    <span class="focus-item">🎯 {{ point }}</span>
                    {% endfor %}
                    {% for reason in review.reasons %}
                    <span class="reason-item">💡 {{ reason }}</span>
                    {% endfor %}
                </div>
            </div>
            
            <!-- 该产业链新闻 -->
            {% for item in review.top_items %}
            <div class="news-item {% if item.priority == 'P1' %}p1{% elif item.priority == 'P2' %}p2{% endif %} {% if item.is_new %}new{% endif %}">
                <div class="news-title">
                    {% if item.link %}<a href="{{ item.link }}" target="_blank">{{ item.title }}</a>{% else %}{{ item.title }}{% endif %}
                </div>
                <div class="news-meta">
                    {% if item.priority == 'P1' %}<span class="meta-tag priority">P1 高优</span>{% elif item.priority == 'P2' %}<span class="meta-tag priority p2">P2 重要</span>{% endif %}
                    <span class="meta-tag event">{{ item.event_type.icon }} {{ item.event_type.name }}</span>
                    {% for company in item.companies[:2] %}<span class="meta-tag company">{{ company }}</span>{% endfor %}
                </div>
                
                <!-- 新闻点评 -->
                {% if item.expert_comment %}
                <div class="news-comment">
                    <div class="focus">🎯 关注点：{{ item.expert_comment.focus_points | join('、') }}</div>
                    <div class="reason">💡 原因：{{ item.expert_comment.reasons | join('；') }}</div>
                </div>
                {% endif %}
                
                {% if item.summary %}
                <div class="news-summary">{{ item.summary[:200] }}{% if item.summary|length > 200 %}...{% endif %}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        {% endfor %}
        
        <!-- 热门公司 -->
        {% if hot_companies %}
        <div class="chain-section">
            <div class="chain-header">
                <div class="left">
                    <span class="icon">🏢</span>
                    <h2>今日热门公司</h2>
                </div>
            </div>
            <div class="hot-companies">
                {% for company in hot_companies %}<span class="company-tag">{{ company }}</span>{% endfor %}
            </div>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>📧 AI日报 · 每日早8点自动推送</p>
            <p>由 popeyeluo 的AI助理自动生成 | 产业链视角</p>
        </div>
    </div>
</body>
</html>'''


def generate_ai_report(analysis_results: Dict) -> str:
    return AIReportGenerator().generate_html_report(analysis_results)
