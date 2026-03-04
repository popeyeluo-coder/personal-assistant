# -*- coding: utf-8 -*-
"""
AI日报系统 - 企业微信推送模块
"""
import os
import requests
from datetime import datetime


class WeComSender:
    """企业微信机器人推送"""
    
    def __init__(self):
        self.webhook_url = os.environ.get(
            "WECOM_WEBHOOK_URL",
            "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ed570230-8df9-4379-abf4-567ace0071de"
        )
    
    def send_markdown(self, content: str) -> bool:
        """
        发送Markdown格式消息
        
        Args:
            content: Markdown内容
        
        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            print("⚠️ 企微Webhook未配置，跳过发送")
            return False
        
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            
            response = requests.post(self.webhook_url, json=data, timeout=30)
            result = response.json()
            
            if result.get("errcode") == 0:
                print("✅ 企微推送成功")
                return True
            else:
                print(f"❌ 企微推送失败: {result.get('errmsg', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"❌ 企微推送异常: {e}")
            return False
    
    def send_daily_report(self, news_summary: dict, date_str: str = None) -> bool:
        """
        发送日报摘要到企微
        
        Args:
            news_summary: 新闻摘要数据
            date_str: 日期字符串
        
        Returns:
            是否发送成功
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y年%m月%d日")
        
        # 构建Markdown内容
        content = self._build_markdown(news_summary, date_str)
        return self.send_markdown(content)
    
    def _build_markdown(self, summary: dict, date_str: str) -> str:
        """构建Markdown格式的日报摘要"""
        lines = [
            f"# 🤖 AI日报 | {date_str}",
            "",
        ]
        
        # 专家总评
        if summary.get("expert_summary"):
            lines.append(f"**📋 今日概览**: {summary['expert_summary'][:200]}")
            lines.append("")
        
        # 统计信息
        total = summary.get("total_news", 0)
        p1_count = summary.get("p1_count", 0)
        lines.append(f"📊 共采集 **{total}** 条新闻，其中 <font color=\"warning\">{p1_count} 条重要</font>")
        lines.append("")
        
        # P1重要新闻（最多5条）
        p1_news = summary.get("p1_news", [])[:5]
        if p1_news:
            lines.append("---")
            lines.append("### 🔥 重要新闻")
            for i, news in enumerate(p1_news, 1):
                title = news.get("title", "")[:60]
                value = news.get("value_rating", "★★★")
                lines.append(f"{i}. [{title}]({news.get('url', '#')}) {value}")
            lines.append("")
        
        # P2值得关注（最多3条）
        p2_news = summary.get("p2_news", [])[:3]
        if p2_news:
            lines.append("### 📌 值得关注")
            for news in p2_news:
                title = news.get("title", "")[:50]
                lines.append(f"- {title}")
            lines.append("")
        
        # 维度分布
        dimensions = summary.get("dimensions", {})
        if dimensions:
            dim_text = " | ".join([f"{k}: {v}" for k, v in list(dimensions.items())[:4]])
            lines.append(f"**维度分布**: {dim_text}")
            lines.append("")
        
        lines.append("> 详细报告已发送至邮箱，请查收 📧")
        
        return "\n".join(lines)
    
    def send_alert(self, title: str, message: str) -> bool:
        """
        发送告警消息
        
        Args:
            title: 告警标题
            message: 告警内容
        
        Returns:
            是否发送成功
        """
        content = f"""# ⚠️ {title}

{message}

> 时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        return self.send_markdown(content)


# 便捷接口
def send_wecom_report(news_summary: dict, date_str: str = None) -> bool:
    """发送报告到企微的便捷接口"""
    sender = WeComSender()
    return sender.send_daily_report(news_summary, date_str)


def send_wecom_alert(title: str, message: str) -> bool:
    """发送告警到企微的便捷接口"""
    sender = WeComSender()
    return sender.send_alert(title, message)


if __name__ == "__main__":
    # 测试发送
    sender = WeComSender()
    test_summary = {
        "expert_summary": "今日AI领域动态活跃，多家大模型厂商发布新版本...",
        "total_news": 50,
        "p1_count": 8,
        "p1_news": [
            {"title": "OpenAI发布GPT-5预览版", "url": "https://example.com", "value_rating": "★★★"},
            {"title": "Claude 4正式开放API", "url": "https://example.com", "value_rating": "★★★"},
        ],
        "p2_news": [
            {"title": "百度文心一言用户突破1亿"},
            {"title": "阿里通义千问开源新版本"},
        ],
        "dimensions": {"技术突破": 10, "产品发布": 15, "商业动态": 8}
    }
    sender.send_daily_report(test_summary)
