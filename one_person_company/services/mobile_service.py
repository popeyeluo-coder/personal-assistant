"""
移动端交互服务
支持：企业微信机器人、Telegram、钉钉
让你随时随地通过手机与系统交互
"""

import os
import json
import logging
import requests
import hashlib
import base64
import hmac
import time
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MobileService:
    """
    移动端推送服务
    支持多种即时通讯渠道
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # 企业微信配置
        self.wechat_webhook = self.config.get("wechat_webhook", "")
        
        # Telegram配置
        self.telegram_token = self.config.get("telegram_token", "")
        self.telegram_chat_id = self.config.get("telegram_chat_id", "")
        
        # 钉钉配置
        self.dingtalk_webhook = self.config.get("dingtalk_webhook", "")
        self.dingtalk_secret = self.config.get("dingtalk_secret", "")
        
    # ==================== 企业微信机器人 ====================
    
    def send_wechat_text(self, content: str, mentioned: List[str] = None) -> Dict:
        """
        发送企业微信文本消息
        
        Args:
            content: 消息内容
            mentioned: @的成员列表，如 ["user1", "@all"]
        """
        if not self.wechat_webhook:
            return {"status": "error", "message": "未配置企业微信Webhook"}
        
        try:
            data = {
                "msgtype": "text",
                "text": {
                    "content": content
                }
            }
            
            if mentioned:
                data["text"]["mentioned_list"] = mentioned
            
            response = requests.post(
                self.wechat_webhook,
                json=data,
                timeout=10
            )
            
            result = response.json()
            if result.get("errcode") == 0:
                logger.info("✅ 企业微信消息发送成功")
                return {"status": "success", "timestamp": datetime.now().isoformat()}
            else:
                return {"status": "error", "message": result.get("errmsg", "")}
                
        except Exception as e:
            logger.error(f"企业微信发送失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_wechat_markdown(self, content: str) -> Dict:
        """
        发送企业微信Markdown消息（更美观）
        
        Markdown语法支持：
        - 标题：# 一级 ## 二级
        - 加粗：**粗体**
        - 链接：[文字](url)
        - 引用：> 引用内容
        - 颜色：<font color="info">绿色</font> <font color="warning">橙色</font>
        """
        if not self.wechat_webhook:
            return {"status": "error", "message": "未配置企业微信Webhook"}
        
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": content
                }
            }
            
            response = requests.post(
                self.wechat_webhook,
                json=data,
                timeout=10
            )
            
            result = response.json()
            if result.get("errcode") == 0:
                logger.info("✅ 企业微信Markdown消息发送成功")
                return {"status": "success", "timestamp": datetime.now().isoformat()}
            else:
                return {"status": "error", "message": result.get("errmsg", "")}
                
        except Exception as e:
            logger.error(f"企业微信发送失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_wechat_card(self, title: str, description: str, url: str, btn_text: str = "查看详情") -> Dict:
        """
        发送企业微信卡片消息
        """
        if not self.wechat_webhook:
            return {"status": "error", "message": "未配置企业微信Webhook"}
        
        try:
            data = {
                "msgtype": "template_card",
                "template_card": {
                    "card_type": "text_notice",
                    "main_title": {
                        "title": title,
                        "desc": description[:30]
                    },
                    "sub_title_text": description,
                    "card_action": {
                        "type": 1,
                        "url": url
                    }
                }
            }
            
            response = requests.post(
                self.wechat_webhook,
                json=data,
                timeout=10
            )
            
            result = response.json()
            if result.get("errcode") == 0:
                return {"status": "success", "timestamp": datetime.now().isoformat()}
            else:
                return {"status": "error", "message": result.get("errmsg", "")}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # ==================== Telegram Bot ====================
    
    def send_telegram_message(self, text: str, parse_mode: str = "Markdown") -> Dict:
        """
        发送Telegram消息
        
        Args:
            text: 消息内容
            parse_mode: 解析模式 (Markdown/HTML)
        """
        if not self.telegram_token or not self.telegram_chat_id:
            return {"status": "error", "message": "未配置Telegram"}
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("ok"):
                logger.info("✅ Telegram消息发送成功")
                return {"status": "success", "timestamp": datetime.now().isoformat()}
            else:
                return {"status": "error", "message": result.get("description", "")}
                
        except Exception as e:
            logger.error(f"Telegram发送失败: {e}")
            return {"status": "error", "message": str(e)}
    
    # ==================== 钉钉机器人 ====================
    
    def _dingtalk_sign(self) -> tuple:
        """生成钉钉签名"""
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.dingtalk_secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.dingtalk_secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return timestamp, sign
    
    def send_dingtalk_text(self, content: str, at_all: bool = False) -> Dict:
        """发送钉钉文本消息"""
        if not self.dingtalk_webhook:
            return {"status": "error", "message": "未配置钉钉Webhook"}
        
        try:
            url = self.dingtalk_webhook
            if self.dingtalk_secret:
                timestamp, sign = self._dingtalk_sign()
                url = f"{url}&timestamp={timestamp}&sign={sign}"
            
            data = {
                "msgtype": "text",
                "text": {"content": content},
                "at": {"isAtAll": at_all}
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                logger.info("✅ 钉钉消息发送成功")
                return {"status": "success", "timestamp": datetime.now().isoformat()}
            else:
                return {"status": "error", "message": result.get("errmsg", "")}
                
        except Exception as e:
            logger.error(f"钉钉发送失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_dingtalk_markdown(self, title: str, content: str) -> Dict:
        """发送钉钉Markdown消息"""
        if not self.dingtalk_webhook:
            return {"status": "error", "message": "未配置钉钉Webhook"}
        
        try:
            url = self.dingtalk_webhook
            if self.dingtalk_secret:
                timestamp, sign = self._dingtalk_sign()
                url = f"{url}&timestamp={timestamp}&sign={sign}"
            
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": content
                }
            }
            
            response = requests.post(url, json=data, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                return {"status": "success", "timestamp": datetime.now().isoformat()}
            else:
                return {"status": "error", "message": result.get("errmsg", "")}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    # ==================== 统一推送接口 ====================
    
    def push_daily_report(self, report_data: Dict) -> Dict:
        """
        推送每日报告到所有配置的渠道
        """
        results = {}
        
        # 格式化报告
        markdown_report = self._format_report_markdown(report_data)
        text_report = self._format_report_text(report_data)
        
        # 推送到企业微信
        if self.wechat_webhook:
            results["wechat"] = self.send_wechat_markdown(markdown_report)
        
        # 推送到Telegram
        if self.telegram_token:
            results["telegram"] = self.send_telegram_message(markdown_report)
        
        # 推送到钉钉
        if self.dingtalk_webhook:
            results["dingtalk"] = self.send_dingtalk_markdown("一人公司日报", markdown_report)
        
        return results
    
    def push_alert(self, alert_type: str, message: str, level: str = "warning") -> Dict:
        """
        推送告警到所有渠道
        
        Args:
            alert_type: 告警类型 (stock/ecommerce/system)
            message: 告警内容
            level: 告警级别 (info/warning/danger)
        """
        level_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "danger": "🚨"
        }
        emoji = level_emoji.get(level, "📢")
        
        formatted_message = f"""
{emoji} **【一人公司告警】**

**类型**: {alert_type}
**级别**: {level.upper()}
**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**内容**:
{message}
"""
        
        results = {}
        
        if self.wechat_webhook:
            results["wechat"] = self.send_wechat_markdown(formatted_message)
        
        if self.telegram_token:
            results["telegram"] = self.send_telegram_message(formatted_message)
        
        if self.dingtalk_webhook:
            results["dingtalk"] = self.send_dingtalk_markdown(f"{emoji} 告警通知", formatted_message)
        
        return results
    
    def push_stock_update(self, stocks: List[Dict]) -> Dict:
        """推送股票行情更新"""
        content = f"""
📈 **股票行情更新** ({datetime.now().strftime('%H:%M')})

"""
        for stock in stocks:
            change = stock.get('change_pct', 0)
            emoji = "🔴" if change < 0 else "🟢" if change > 0 else "⚪"
            content += f"{emoji} **{stock['name']}** ({stock['code']}): {stock['price']}元 ({change:+.2f}%)\n"
        
        results = {}
        
        if self.wechat_webhook:
            results["wechat"] = self.send_wechat_markdown(content)
        
        return results
    
    def _format_report_markdown(self, data: Dict) -> str:
        """格式化报告为Markdown"""
        return f"""
# 🏢 一人公司日报
> {datetime.now().strftime('%Y年%m月%d日')}

## 📊 今日概览
- 系统状态: <font color="info">正常运行</font>
- AI专家团队: 7人全员在岗

## 📈 股票监控
{self._format_stocks_md(data.get('stocks', []))}

## 🛒 电商趋势
{self._format_trends_md(data.get('trends', []))}

## 🎯 今日建议
1. 关注市场热点
2. 监控股票异动
3. 优化选品策略

---
*一人公司 AI Agent System*
"""
    
    def _format_stocks_md(self, stocks: List[Dict]) -> str:
        """格式化股票列表"""
        if not stocks:
            return "- 暂无数据"
        
        lines = []
        for s in stocks:
            change = s.get('change_pct', 0)
            color = "warning" if change < 0 else "info" if change > 0 else "comment"
            lines.append(f"- {s['name']}: <font color=\"{color}\">{s.get('price', 'N/A')}元 ({change:+.2f}%)</font>")
        return "\n".join(lines)
    
    def _format_trends_md(self, trends: List[Dict]) -> str:
        """格式化趋势列表"""
        if not trends:
            return "- 暂无数据"
        
        lines = []
        for i, t in enumerate(trends[:3], 1):
            lines.append(f"{i}. {t.get('title', '未知')[:30]}...")
        return "\n".join(lines)
    
    def _format_report_text(self, data: Dict) -> str:
        """格式化报告为纯文本"""
        return f"""
🏢 一人公司日报 - {datetime.now().strftime('%Y年%m月%d日')}

📊 系统状态: 正常运行
🤖 AI专家团队: 7人全员在岗

📈 股票监控:
{self._format_stocks_text(data.get('stocks', []))}

🎯 今日建议:
1. 关注市场热点
2. 监控股票异动
3. 优化选品策略
"""
    
    def _format_stocks_text(self, stocks: List[Dict]) -> str:
        """格式化股票为纯文本"""
        if not stocks:
            return "  暂无数据"
        
        lines = []
        for s in stocks:
            change = s.get('change_pct', 0)
            emoji = "📉" if change < 0 else "📈" if change > 0 else "➖"
            lines.append(f"  {emoji} {s['name']}: {s.get('price', 'N/A')}元 ({change:+.2f}%)")
        return "\n".join(lines)


# 快速测试
if __name__ == "__main__":
    # 测试企业微信（需要配置webhook）
    service = MobileService({
        "wechat_webhook": ""  # 填入你的企业微信机器人webhook
    })
    
    # 测试发送
    # result = service.send_wechat_text("测试消息 from 一人公司")
    # print(result)
