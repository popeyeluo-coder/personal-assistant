# -*- coding: utf-8 -*-
"""
AI日报系统 - 企业微信推送模块（增强版）
展示完整新闻列表、专业点评、可点击链接
按AI产业链分类展示：硬件/芯片、基础模型、应用层等
"""
import os
import sys
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import WECOM_CONFIG
    DEFAULT_WEBHOOK = WECOM_CONFIG.get("webhook_url", "")
except:
    DEFAULT_WEBHOOK = ""


class WeComSender:
    """企业微信机器人推送（增强版）"""
    
    def __init__(self):
        self.webhook_url = os.environ.get("WECOM_WEBHOOK_URL") or DEFAULT_WEBHOOK or \
            "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ed570230-8df9-4379-abf4-567ace0071de"
    
    def send_markdown(self, content: str) -> bool:
        """发送Markdown格式消息"""
        if not self.webhook_url:
            print("⚠️ 企微Webhook未配置，跳过发送")
            return False
        
        try:
            # 企微markdown有4096字符限制
            if len(content) > 4000:
                content = content[:3900] + "\n\n> ⚠️ 内容过长已截断，完整报告请查看邮箱"
            
            data = {"msgtype": "markdown", "markdown": {"content": content}}
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
    
    def send_daily_report(self, analysis_results: Dict, date_str: str = None) -> bool:
        """
        发送日报到企微（包含完整新闻和专业点评）
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y年%m月%d日")
        
        # 兼容旧格式
        if isinstance(analysis_results, str):
            return self._send_simple_report(analysis_results, date_str)
        
        content = self._build_rich_report(analysis_results, date_str)
        return self.send_markdown(content)
    
    def _send_simple_report(self, html_content: str, date_str: str) -> bool:
        """兼容旧格式"""
        content = f"""# 🤖 AI日报 | {date_str}

📧 完整报告已发送至邮箱，请查收。"""
        return self.send_markdown(content)
    
    def _build_rich_report(self, results: Dict, date_str: str) -> str:
        """构建富内容报告（控制在4000字符以内）"""
        items = results.get("items", [])
        overall_review = results.get("overall_review", {})
        chain_reviews = results.get("chain_reviews", {})
        summary = results.get("summary", {})
        
        lines = [
            f"# 🤖 AI日报 | {date_str}",
            "",
        ]
        
        # 统计概览
        total = len(items)
        p1_count = summary.get("priority_counts", {}).get("P1", 0)
        p2_count = summary.get("priority_counts", {}).get("P2", 0)
        
        lines.append(f"📊 共 **{total}** 条 | <font color=\"warning\">{p1_count} 高优</font> | {p2_count} 重要")
        lines.append("")
        
        # ===== 整体点评（精简版）=====
        if overall_review:
            overview_text = overall_review.get('overview', '')[:150]
            lines.append(f"> {overview_text}")
            lines.append("")
            
            focus_points = overall_review.get("focus_points", [])[:3]
            if focus_points:
                lines.append("**🎯 关注点：**" + " | ".join(focus_points[:2]))
                lines.append("")
        
        # ===== 高优新闻（P1）最多5条 =====
        p1_items = [i for i in items if i.get("priority") == "P1"][:5]
        if p1_items:
            lines.append("---")
            lines.append("## 🔥 高优必读")
            lines.append("")
            
            for i, item in enumerate(p1_items, 1):
                title = item.get("title", "")[:50]
                url = item.get("link", "") or item.get("url", "") or "#"
                chain = item.get("chain", {}).get("name", "AI")
                
                lines.append(f"**{i}. [{title}]({url})** `{chain}`")
            lines.append("")
        
        # ===== 按产业链展示（最多3个产业链，每个2条）=====
        lines.append("---")
        lines.append("## 📈 产业链要闻")
        lines.append("")
        
        shown_chains = 0
        for chain_key, review in chain_reviews.items():
            if shown_chains >= 3:
                break
            
            if review.get("total", 0) == 0:
                continue
            
            top_items = review.get("top_items", [])[:2]
            if not top_items:
                continue
            
            shown_chains += 1
            chain_name = review.get("name", "")
            chain_icon = review.get("icon", "📰")
            
            lines.append(f"**{chain_icon} {chain_name}**")
            for item in top_items:
                title = item.get("title", "")[:40]
                url = item.get("link", "") or item.get("url", "") or "#"
                lines.append(f"• [{title}]({url})")
            lines.append("")
        
        # ===== 热门公司 =====
        hot_companies = summary.get("hot_companies", [])[:5]
        if hot_companies:
            lines.append(f"🏢 **热门**: {' | '.join(hot_companies)}")
            lines.append("")
        
        lines.append("> 📧 详细报告已发邮箱")
        
        return "\n".join(lines)
    
    def send_alert(self, title: str, message: str) -> bool:
        """发送告警消息"""
        content = f"""# ⚠️ {title}

{message}

> 时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        return self.send_markdown(content)


def send_wecom_report(analysis_results: Dict, date_str: str = None) -> bool:
    return WeComSender().send_daily_report(analysis_results, date_str)


def send_wecom_alert(title: str, message: str) -> bool:
    return WeComSender().send_alert(title, message)
