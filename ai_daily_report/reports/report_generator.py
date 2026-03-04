# -*- coding: utf-8 -*-
"""
AI日报系统 - 报告生成模块
生成精美的HTML格式日报邮件
"""
import sys
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
from jinja2 import Template

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import STORAGE_CONFIG


class AIReportGenerator:
    """AI日报报告生成器"""
    
    def __init__(self):
        self.report_dir = Path(__file__).parent.parent / STORAGE_CONFIG["report_dir"]
        self.report_dir.mkdir(exist_ok=True)
    
    def generate_html_report(self, analysis_results: Dict) -> str:
        """
        生成HTML格式的日报邮件
        
        Args:
            analysis_results: 分析结果
        
        Returns:
            HTML内容字符串
        """
        template = Template(self._get_daily_report_template())
        
        items = analysis_results.get("items", [])
        summary = analysis_results.get("summary", {})
        expert_overview = analysis_results.get("expert_overview", {})
        
        # 按优先级分组
        p1_items = [item for item in items if item.get("priority") == "P1"]
        p2_items = [item for item in items if item.get("priority") == "P2"]
        p3_items = [item for item in items if item.get("priority") in ["P3", "P4"]]
        
        # 按维度分组
        dimension_groups = {}
        for item in items:
            dim_name = item.get("dimension", {}).get("name", "其他动态")
            if dim_name not in dimension_groups:
                dimension_groups[dim_name] = {
                    "name": dim_name,
                    "icon": item.get("dimension", {}).get("icon", "📰"),
                    "items": [],
                }
            dimension_groups[dim_name]["items"].append(item)
        
        # 准备模板上下文
        today = datetime.now()
        context = {
            "report_date": today.strftime("%Y年%m月%d日"),
            "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][today.weekday()],
            "total_items": len(items),
            
            # 专家总评
            "expert_overview": expert_overview,
            
            # 按优先级分组
            "p1_items": p1_items[:10],
            "p2_items": p2_items[:8],
            "p3_items": p3_items[:6],
            
            # 按维度分组
            "dimension_groups": list(dimension_groups.values()),
            
            # 统计信息
            "summary": summary,
            "hot_companies": summary.get("hot_companies", [])[:8],
            "new_count": summary.get("new_count", 0),
            "priority_counts": summary.get("priority_counts", {}),
        }
        
        html_content = template.render(**context)
        
        # 保存报告
        self._save_report(html_content, today)
        
        return html_content
    
    def _save_report(self, html_content: str, date: datetime):
        """保存报告到文件"""
        filename = f"ai_daily_{date.strftime('%Y%m%d')}.html"
        filepath = self.report_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"   ✓ 报告已保存: {filepath}")
    
    def _get_daily_report_template(self) -> str:
        """获取日报HTML模板"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI日报 - {{ report_date }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* 头部样式 */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .header .date {
            font-size: 16px;
            opacity: 0.9;
        }
        
        .header .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
        }
        
        .header .stat-item {
            text-align: center;
        }
        
        .header .stat-value {
            font-size: 24px;
            font-weight: bold;
        }
        
        .header .stat-label {
            font-size: 12px;
            opacity: 0.8;
        }
        
        /* 专家总评卡片 */
        .expert-card {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            color: white;
        }
        
        .expert-card .title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 12px;
        }
        
        .expert-card .risk-badge {
            font-size: 11px;
            padding: 3px 10px;
            border-radius: 12px;
            background: rgba(255,255,255,0.2);
        }
        
        .expert-card .overview {
            font-size: 14px;
            line-height: 1.8;
            margin-bottom: 15px;
        }
        
        .expert-card .section {
            background: rgba(255,255,255,0.15);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
        }
        
        .expert-card .section-title {
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 8px;
            opacity: 0.9;
        }
        
        .expert-card .section-item {
            font-size: 12px;
            padding: 4px 0;
            opacity: 0.95;
        }
        
        /* 新闻卡片 */
        .news-section {
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .section-header h2 {
            font-size: 18px;
            color: #333;
        }
        
        .section-header .count {
            background: #667eea;
            color: white;
            font-size: 12px;
            padding: 2px 8px;
            border-radius: 10px;
        }
        
        /* 新闻条目 */
        .news-item {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 12px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            transition: transform 0.2s;
        }
        
        .news-item:hover {
            transform: translateX(5px);
        }
        
        .news-item.p1 {
            border-left-color: #dc3545;
            background: #fff5f5;
        }
        
        .news-item.p2 {
            border-left-color: #fd7e14;
            background: #fff8f0;
        }
        
        .news-item.new {
            position: relative;
        }
        
        .news-item.new::before {
            content: "新";
            position: absolute;
            top: -5px;
            right: 10px;
            background: #dc3545;
            color: white;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 8px;
        }
        
        .news-title {
            font-size: 15px;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        
        .news-title a {
            color: #333;
            text-decoration: none;
        }
        
        .news-title a:hover {
            color: #667eea;
        }
        
        .news-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 10px;
        }
        
        .meta-tag {
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 4px;
            background: #e9ecef;
            color: #666;
        }
        
        .meta-tag.priority-1 {
            background: #dc3545;
            color: white;
        }
        
        .meta-tag.priority-2 {
            background: #fd7e14;
            color: white;
        }
        
        .meta-tag.dimension {
            background: #667eea;
            color: white;
        }
        
        .meta-tag.company {
            background: #28a745;
            color: white;
        }
        
        .meta-tag.new {
            background: #dc3545;
            color: white;
        }
        
        .news-comment {
            font-size: 12px;
            color: #666;
            padding: 8px 12px;
            background: white;
            border-radius: 6px;
            border-left: 3px solid #667eea;
            margin-top: 8px;
        }
        
        .news-summary {
            font-size: 13px;
            color: #666;
            margin-top: 8px;
            line-height: 1.6;
        }
        
        /* 热门公司 */
        .hot-companies {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }
        
        .company-tag {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 12px;
        }
        
        /* 页脚 */
        .footer {
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 12px;
        }
        
        /* 简洁列表样式 */
        .simple-list {
            margin: 0;
            padding: 0;
            list-style: none;
        }
        
        .simple-list li {
            padding: 10px 12px;
            border-bottom: 1px solid #f0f0f0;
            font-size: 13px;
        }
        
        .simple-list li:last-child {
            border-bottom: none;
        }
        
        .simple-list .title {
            color: #333;
        }
        
        .simple-list .meta {
            font-size: 11px;
            color: #999;
            margin-top: 4px;
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
                <div class="stat-item">
                    <div class="stat-value">{{ total_items }}</div>
                    <div class="stat-label">今日新闻</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ priority_counts.get('P1', 0) }}</div>
                    <div class="stat-label">高优</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ new_count }}</div>
                    <div class="stat-label">新信息</div>
                </div>
            </div>
        </div>
        
        <!-- 专家总评 -->
        {% if expert_overview %}
        <div class="expert-card">
            <div class="title">
                <span>🎯 今日专家总评</span>
                <span class="risk-badge" style="background: {{ expert_overview.risk_color }};">{{ expert_overview.risk_level }}关注度</span>
            </div>
            <div class="overview">{{ expert_overview.overview }}</div>
            
            {% if expert_overview.key_trends %}
            <div class="section">
                <div class="section-title">📈 关键趋势</div>
                {% for trend in expert_overview.key_trends %}
                <div class="section-item">{{ trend }}</div>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if expert_overview.recommendations %}
            <div class="section">
                <div class="section-title">💡 今日建议</div>
                {% for rec in expert_overview.recommendations %}
                <div class="section-item">→ {{ rec }}</div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <!-- 高优新闻 P1 -->
        {% if p1_items %}
        <div class="news-section">
            <div class="section-header">
                <h2>🔥 高优必读</h2>
                <span class="count">{{ p1_items|length }}条</span>
            </div>
            
            {% for item in p1_items %}
            <div class="news-item p1 {% if item.is_new %}new{% endif %}">
                <div class="news-title">
                    {% if item.link %}
                    <a href="{{ item.link }}" target="_blank">{{ item.title }}</a>
                    {% else %}
                    {{ item.title }}
                    {% endif %}
                </div>
                <div class="news-meta">
                    <span class="meta-tag priority-1">P1</span>
                    <span class="meta-tag dimension">{{ item.dimension.icon }} {{ item.dimension.name }}</span>
                    {% for company in item.companies[:2] %}
                    <span class="meta-tag company">{{ company }}</span>
                    {% endfor %}
                    {% if item.source %}<span class="meta-tag">{{ item.source }}</span>{% endif %}
                </div>
                {% if item.brief_comment %}
                <div class="news-comment">{{ item.brief_comment }}</div>
                {% endif %}
                {% if item.summary %}
                <div class="news-summary">{{ item.summary[:150] }}{% if item.summary|length > 150 %}...{% endif %}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <!-- 重要新闻 P2 -->
        {% if p2_items %}
        <div class="news-section">
            <div class="section-header">
                <h2>📌 重要关注</h2>
                <span class="count">{{ p2_items|length }}条</span>
            </div>
            
            {% for item in p2_items %}
            <div class="news-item p2 {% if item.is_new %}new{% endif %}">
                <div class="news-title">
                    {% if item.link %}
                    <a href="{{ item.link }}" target="_blank">{{ item.title[:60] }}{% if item.title|length > 60 %}...{% endif %}</a>
                    {% else %}
                    {{ item.title[:60] }}{% if item.title|length > 60 %}...{% endif %}
                    {% endif %}
                </div>
                <div class="news-meta">
                    <span class="meta-tag priority-2">P2</span>
                    <span class="meta-tag dimension">{{ item.dimension.icon }} {{ item.dimension.name }}</span>
                    {% for company in item.companies[:1] %}
                    <span class="meta-tag company">{{ company }}</span>
                    {% endfor %}
                </div>
                {% if item.brief_comment %}
                <div class="news-comment">{{ item.brief_comment }}</div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <!-- 一般新闻 P3/P4 -->
        {% if p3_items %}
        <div class="news-section">
            <div class="section-header">
                <h2>📋 其他动态</h2>
                <span class="count">{{ p3_items|length }}条</span>
            </div>
            
            <ul class="simple-list">
            {% for item in p3_items %}
                <li>
                    <div class="title">
                        {% if item.link %}
                        <a href="{{ item.link }}" target="_blank" style="color:#333;text-decoration:none;">
                            {{ item.dimension.icon }} {{ item.title[:50] }}{% if item.title|length > 50 %}...{% endif %}
                        </a>
                        {% else %}
                        {{ item.dimension.icon }} {{ item.title[:50] }}{% if item.title|length > 50 %}...{% endif %}
                        {% endif %}
                    </div>
                    <div class="meta">{{ item.brief_comment }}</div>
                </li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        <!-- 热门公司 -->
        {% if hot_companies %}
        <div class="news-section">
            <div class="section-header">
                <h2>🏢 今日热门公司</h2>
            </div>
            <div class="hot-companies">
                {% for company in hot_companies %}
                <span class="company-tag">{{ company }}</span>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        <!-- 页脚 -->
        <div class="footer">
            <p>📧 AI日报 · 每日早8点自动推送</p>
            <p>由 popeyeluo 的AI助理自动生成</p>
        </div>
    </div>
</body>
</html>'''


# 便捷接口
def generate_ai_report(analysis_results: Dict) -> str:
    """生成AI日报的便捷接口"""
    generator = AIReportGenerator()
    return generator.generate_html_report(analysis_results)


if __name__ == "__main__":
    # 测试
    test_results = {
        "items": [
            {
                "title": "OpenAI发布GPT-5",
                "summary": "重大突破",
                "link": "https://example.com",
                "dimension": {"name": "技术突破", "icon": "🔬"},
                "priority": "P1",
                "importance": {"level": "high"},
                "companies": ["OpenAI"],
                "brief_comment": "⚡ 高价值 | 重大技术突破",
                "is_new": True,
            }
        ],
        "summary": {
            "hot_companies": ["OpenAI", "Google"],
            "new_count": 1,
            "priority_counts": {"P1": 1},
        },
        "expert_overview": {
            "overview": "今日AI领域动态活跃。",
            "key_trends": ["技术突破活跃"],
            "recommendations": ["关注OpenAI动态"],
            "risk_level": "高",
            "risk_color": "#dc3545",
        },
    }
    
    html = generate_ai_report(test_results)
    print(f"生成报告长度: {len(html)} 字符")
