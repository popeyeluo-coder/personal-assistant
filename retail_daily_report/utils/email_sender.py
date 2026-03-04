# -*- coding: utf-8 -*-
"""
零售日报 - 邮件发送模块
"""
import os
import sys
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EMAIL_CONFIG


class EmailSender:
    def __init__(self):
        self.smtp_server = EMAIL_CONFIG["smtp_server"]
        self.smtp_port = EMAIL_CONFIG["smtp_port"]
        self.sender_email = EMAIL_CONFIG["sender_email"]
        self.sender_password = EMAIL_CONFIG["sender_password"]
        self.receiver_emails = EMAIL_CONFIG["receiver_emails"]
        self.subject_template = EMAIL_CONFIG["subject_template"]
    
    def send_daily_report(self, html_content: str, date_str: str = None) -> bool:
        if date_str is None:
            date_str = datetime.now().strftime("%Y年%m月%d日")
        subject = self.subject_template.format(date=date_str)
        return self._send_email(html_content, subject)
    
    def _send_email(self, html_content: str, subject: str) -> bool:
        if not self.sender_password or not self.receiver_emails:
            print("⚠️ 邮件配置不完整，跳过发送")
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = ", ".join(self.receiver_emails)
            message.attach(MIMEText(html_content, "html", "utf-8"))
            
            # 发送邮件的内部函数
            def do_send(ctx):
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=ctx) as server:
                    server.login(self.sender_email, self.sender_password)
                    server.sendmail(self.sender_email, self.receiver_emails, message.as_string())
            
            # 首先尝试使用默认SSL上下文
            try:
                context = ssl.create_default_context()
                do_send(context)
            except ssl.SSLCertVerificationError:
                # 证书验证失败时，使用不验证证书的方式重试
                print("   ⚠️ SSL证书验证失败，尝试跳过验证...")
                context = ssl._create_unverified_context()
                do_send(context)
            
            print(f"✅ 邮件发送成功: {subject}")
            return True
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False


def send_report(html_content: str, date_str: str = None) -> bool:
    return EmailSender().send_daily_report(html_content, date_str)
