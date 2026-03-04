# -*- coding: utf-8 -*-
"""
零售日报系统 - 企业微信推送模块
推送包含重要新闻详情，无需查看邮箱即可了解核心内容
"""
import os
import sys
import requests
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import WECOM_CONFIG
    DEFAULT_WEBHOOK = WECOM_CONFIG.get("webhook_url", "")
except:
    DEFAULT_WEBHOOK = ""


class WeComSender:
    """企业微信机器人推送"""
    
    def __init__(self):
        self.webhook_url = os.environ.get("WECOM_WEBHOOK_URL") or DEFAULT_WEBHOOK or \
            "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ed570230-8df9-4379-abf4-567ace0071de"
    
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
        发送日报摘要到企微（包含重要新闻详情）
        
        Args:
            news_summary: 新闻摘要数据
            date_str: 日期字符串
        
        Returns:
            是否发送成功
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y年%m月%d日")
        
        # 构建Markdown内容
        content = self._build_rich_markdown(news_summary, date_str)
        return self.send_markdown(content)
    
    def _build_rich_markdown(self, summary: dict, date_str: str) -> str:
        """构建富内容Markdown格式的日报（包含新闻详情）"""
        lines = [
            f"# 🛒 零售日报 | {date_str}",
            "",
        ]
        
        # 统计信息
        total = summary.get("total_news", 0)
        p1_count = summary.get("p1_count", 0)
        lines.append(f"📊 共采集 **{total}** 条新闻，<font color=\"warning\">{p1_count} 条重要</font>")
        lines.append("")
        
        # 专家总评（如果有）
        expert_summary = summary.get("expert_summary", "")
        if expert_summary:
            lines.append(f"**📋 今日概览**")
            lines.append(f"> {expert_summary[:300]}")
            lines.append("")
        
        # P1重要新闻（展示详情，最多6条）
        p1_news = summary.get("p1_news", [])[:6]
        if p1_news:
            lines.append("---")
            lines.append("## 🔥 重要新闻")
            lines.append("")
            
            for i, news in enumerate(p1_news, 1):
                title = news.get("title", "")[:80]
                url = news.get("url", "#")
                value = news.get("value_rating", "★★★")
                comment = news.get("comment", "")[:100] if news.get("comment") else ""
                source = news.get("source", "")
                description = news.get("description", "")[:150] if news.get("description") else ""
                
                lines.append(f"**{i}. [{title}]({url})**")
                if source:
                    lines.append(f"   来源: {source} | 价值度: {value}")
                if description:
                    lines.append(f"   > {description}")
                if comment:
                    lines.append(f"   💡 *{comment}*")
                lines.append("")
        
        # P2值得关注（最多4条，带简介）
        p2_news = summary.get("p2_news", [])[:4]
        if p2_news:
            lines.append("---")
            lines.append("## 📌 值得关注")
            lines.append("")
            for news in p2_news:
                title = news.get("title", "")[:60]
                url = news.get("url", "#")
                description = news.get("description", "")[:80] if news.get("description") else ""
                if description:
                    lines.append(f"- [{title}]({url})")
                    lines.append(f"  > {description}")
                else:
                    lines.append(f"- [{title}]({url})")
            lines.append("")
        
        # 业态分布
        dimensions = summary.get("dimensions", {})
        if dimensions:
            lines.append("---")
            dim_items = list(dimensions.items())[:5]
            dim_text = " | ".join([f"**{k}**: {v}" for k, v in dim_items])
            lines.append(f"📈 {dim_text}")
            lines.append("")
        
        # 底部提示
        lines.append("> 📧 完整报告已发送至邮箱")
        
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
        "expert_summary": "今日零售行业动态活跃，便利店和会员店赛道持续扩张，多家企业发布新战略。",
        "total_news": 36,
        "p1_count": 5,
        "p1_news": [
            {
                "title": "山姆会员店宣布2026年新增10家门店计划",
                "url": "https://example.com/1",
                "value_rating": "★★★",
                "source": "联商网",
                "description": "山姆计划在一二线城市持续扩张，加速布局中国市场",
                "comment": "会员店赛道竞争加剧"
            },
            {
                "title": "盒马鲜生推出新零售3.0战略，全面升级供应链",
                "url": "https://example.com/2",
                "value_rating": "★★★",
                "source": "36氪",
                "description": "盒马将重点打造自有品牌，提升商品力和供应链效率",
                "comment": "新零售进入深水区"
            },
        ],
        "p2_news": [
            {"title": "永辉超市完成供应链数字化升级", "url": "https://example.com/3", "description": "传统商超加速数字化转型"},
            {"title": "7-11便利店进入西南市场", "url": "https://example.com/4", "description": "便利店巨头持续下沉"},
        ],
        "dimensions": {"开店扩张": 10, "业态创新": 8, "供应链": 5, "融资并购": 3}
    }
    sender.send_daily_report(test_summary)
