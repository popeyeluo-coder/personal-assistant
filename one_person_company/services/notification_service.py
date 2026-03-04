"""
通知服务 - 邮件和消息推送
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Dict, List, Optional
from datetime import datetime
import requests
import json

logger = logging.getLogger(__name__)


class NotificationService:
    """
    通知服务
    支持：QQ邮件、企业微信机器人
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # 邮件配置
        self.smtp_server = self.config.get("smtp_server", "smtp.qq.com")
        self.smtp_port = self.config.get("smtp_port", 465)
        self.email_username = self.config.get("username", "709703094@qq.com")
        self.email_auth_code = self.config.get("auth_code", "")
        
        # 企业微信配置
        self.wechat_webhook = self.config.get("wechat_webhook", "")
        
    def send_email(self, 
                   to: str, 
                   subject: str, 
                   content: str, 
                   content_type: str = "html") -> Dict:
        """
        发送邮件
        
        Args:
            to: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型 (html/plain)
        """
        if not self.email_auth_code:
            return {"status": "error", "message": "未配置邮箱授权码"}
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            # 修复 From 头格式，符合 RFC5322 标准
            msg['From'] = f"{self.email_username}"
            msg['To'] = to
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 添加正文
            msg.attach(MIMEText(content, content_type, 'utf-8'))
            
            # 发送
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.email_username, self.email_auth_code)
                server.sendmail(self.email_username, [to], msg.as_string())
            
            logger.info(f"📧 邮件发送成功: {subject} -> {to}")
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "to": to,
                "subject": subject
            }
            
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def send_daily_report(self, report: str, to: str = None) -> Dict:
        """发送每日报告"""
        to = to or self.email_username
        subject = f"【一人公司】每日运营报告 - {datetime.now().strftime('%Y-%m-%d')}"
        
        # 转换为HTML格式
        html_content = self._markdown_to_html(report)
        
        return self.send_email(to, subject, html_content, "html")
    
    def send_alert(self, alert_type: str, message: str, to: str = None) -> Dict:
        """发送紧急告警"""
        to = to or self.email_username
        
        alert_emojis = {
            "risk": "⚠️",
            "opportunity": "💡",
            "system": "🔧",
            "trade": "📈"
        }
        emoji = alert_emojis.get(alert_type, "📢")
        
        subject = f"{emoji}【一人公司告警】{alert_type.upper()}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #e74c3c;">{emoji} 告警通知</h2>
            <div style="background: #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>类型:</strong> {alert_type}<br>
                <strong>时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                <strong>内容:</strong><br>
                <p>{message}</p>
            </div>
            <p style="color: #7f8c8d; font-size: 12px;">
                此邮件由一人公司AI系统自动发送
            </p>
        </body>
        </html>
        """
        
        return self.send_email(to, subject, html_content, "html")
    
    def send_wechat_message(self, content: str, msg_type: str = "text") -> Dict:
        """
        发送企业微信消息
        
        Args:
            content: 消息内容
            msg_type: 消息类型 (text/markdown)
        """
        if not self.wechat_webhook:
            return {"status": "error", "message": "未配置企业微信Webhook"}
        
        try:
            data = {
                "msgtype": msg_type,
                msg_type: {
                    "content": content
                }
            }
            
            response = requests.post(
                self.wechat_webhook,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("errcode") == 0:
                    logger.info("企业微信消息发送成功")
                    return {"status": "success", "timestamp": datetime.now().isoformat()}
                else:
                    return {"status": "error", "message": result.get("errmsg", "")}
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"企业微信消息发送失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def _markdown_to_html(self, markdown_text: str) -> str:
        """简单的Markdown转HTML"""
        html = markdown_text
        
        # 标题
        html = html.replace("# ", "<h1>").replace("\n", "</h1>\n", 1)
        html = html.replace("## ", "<h2>").replace("\n", "</h2>\n")
        html = html.replace("### ", "<h3>").replace("\n", "</h3>\n")
        
        # 列表
        lines = html.split('\n')
        new_lines = []
        in_list = False
        
        for line in lines:
            if line.strip().startswith("- "):
                if not in_list:
                    new_lines.append("<ul>")
                    in_list = True
                new_lines.append(f"<li>{line.strip()[2:]}</li>")
            else:
                if in_list:
                    new_lines.append("</ul>")
                    in_list = False
                new_lines.append(line)
        
        if in_list:
            new_lines.append("</ul>")
        
        html = '\n'.join(new_lines)
        
        # 粗体
        import re
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # 换行
        html = html.replace('\n', '<br>\n')
        
        # 包装
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; max-width: 800px; margin: 0 auto; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
                h2 {{ color: #34495e; }}
                h3 {{ color: #7f8c8d; }}
                ul {{ background: #ecf0f1; padding: 15px 30px; border-radius: 5px; }}
                li {{ margin: 5px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #bdc3c7; padding: 8px; text-align: left; }}
                th {{ background: #3498db; color: white; }}
            </style>
        </head>
        <body>
            {html}
            <hr>
            <p style="color: #95a5a6; font-size: 12px;">
                此邮件由一人公司AI系统自动发送 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </body>
        </html>
        """
    
    def send_trade_notification(self, trade_info: Dict, to: str = None) -> Dict:
        """发送交易通知"""
        to = to or self.email_username
        
        action = trade_info.get("action", "")
        stock = trade_info.get("stock", "")
        price = trade_info.get("price", 0)
        quantity = trade_info.get("quantity", 0)
        
        subject = f"📈【一人公司】交易通知 - {action} {stock}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>📈 交易通知</h2>
            <table style="border-collapse: collapse; width: 100%;">
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; background: #f9f9f9;"><strong>操作</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{action}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; background: #f9f9f9;"><strong>股票</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{stock}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; background: #f9f9f9;"><strong>价格</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{price}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; background: #f9f9f9;"><strong>数量</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{quantity}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px; background: #f9f9f9;"><strong>时间</strong></td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>
                </tr>
            </table>
            <p style="color: #e74c3c; margin-top: 20px;">
                ⚠️ 请确认此交易是否需要执行
            </p>
        </body>
        </html>
        """
        
        return self.send_email(to, subject, html_content, "html")


# 测试
if __name__ == "__main__":
    # 需要配置auth_code才能测试
    service = NotificationService({
        "auth_code": ""  # 填入QQ邮箱授权码测试
    })
    
    # 测试发送报告
    test_report = """
# 一人公司每日报告

## 业务概览
- 电商: 正常运营
- 金融: 持仓稳定

## 今日任务
- 选品分析完成
- 供应商对接中
    """
    
    print("测试邮件发送...")
    # result = service.send_daily_report(test_report)
    # print(result)
