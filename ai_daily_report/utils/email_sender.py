# -*- coding: utf-8 -*-
"""
AI日报系统 - 邮件发送模块
"""
import os
import sys
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import EMAIL_CONFIG


class EmailSender:
    """邮件发送器"""
    
    def __init__(self):
        self.smtp_server = EMAIL_CONFIG["smtp_server"]
        self.smtp_port = EMAIL_CONFIG["smtp_port"]
        self.sender_email = EMAIL_CONFIG["sender_email"]
        self.sender_password = EMAIL_CONFIG["sender_password"]
        self.receiver_emails = EMAIL_CONFIG["receiver_emails"]
        self.subject_template = EMAIL_CONFIG["subject_template"]
    
    def send_daily_report(self, html_content: str, date_str: str = None) -> bool:
        """
        发送日报邮件
        
        Args:
            html_content: HTML格式的报告内容
            date_str: 日期字符串（可选）
        
        Returns:
            是否发送成功
        """
        if date_str is None:
            date_str = datetime.now().strftime("%Y年%m月%d日")
        
        subject = self.subject_template.format(date=date_str)
        return self._send_email(html_content, subject)
    
    def _send_email(self, html_content: str, subject: str) -> bool:
        """
        发送邮件核心逻辑
        
        Args:
            html_content: HTML内容
            subject: 邮件主题
        
        Returns:
            是否发送成功
        """
        if not self.sender_password:
            print("⚠️ 邮件密码未配置，跳过发送")
            return False
        
        if not self.receiver_emails:
            print("⚠️ 收件人未配置，跳过发送")
            return False
        
        try:
            # 创建邮件
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = ", ".join(self.receiver_emails)
            
            # 添加HTML内容
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)
            
            # 使用SSL发送
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    self.receiver_emails,
                    message.as_string()
                )
            
            print(f"✅ 邮件发送成功: {subject}")
            print(f"   收件人: {', '.join(self.receiver_emails)}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("❌ 邮件发送失败: SMTP认证错误，请检查邮箱授权码")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ 邮件发送失败: SMTP错误 - {e}")
            return False
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """发送测试邮件"""
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 20px; border-radius: 10px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 AI日报系统测试</h1>
                <p>这是一封测试邮件，如果您收到此邮件，说明邮件配置正确！</p>
            </div>
            <p>测试时间: {}</p>
        </body>
        </html>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        return self._send_email(test_html, "【AI日报】系统测试邮件")


# 便捷接口
def send_report(html_content: str, date_str: str = None) -> bool:
    """发送报告的便捷接口"""
    sender = EmailSender()
    return sender.send_daily_report(html_content, date_str)


if __name__ == "__main__":
    # 测试发送
    sender = EmailSender()
    sender.send_test_email()
