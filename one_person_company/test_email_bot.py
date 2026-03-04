#!/usr/bin/env python3
"""
测试邮件机器人 - 发送欢迎邮件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
import yaml

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config/api_keys.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def send_welcome_email():
    config = load_config()
    email_config = config.get('notification', {}).get('email', {})
    
    username = email_config.get('username', '')
    auth_code = email_config.get('auth_code', '')
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = username
    msg['Subject'] = Header('🎉 邮件机器人已启动 - 使用指南', 'utf-8')
    
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
            }}
            .content {{
                padding: 30px;
            }}
            .command-box {{
                background: #f8f9fa;
                border-left: 4px solid #667eea;
                padding: 15px;
                margin: 15px 0;
                border-radius: 0 8px 8px 0;
            }}
            .command {{
                font-family: Monaco, Consolas, monospace;
                background: #e9ecef;
                padding: 3px 8px;
                border-radius: 4px;
                color: #495057;
            }}
            .tip {{
                background: #fff3cd;
                border: 1px solid #ffc107;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #6c757d;
                font-size: 14px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #dee2e6;
            }}
            th {{
                background: #f8f9fa;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 邮件机器人已启动</h1>
                <p>一人公司AI系统 - 邮件交互服务</p>
            </div>
            
            <div class="content">
                <h2>📧 如何使用？</h2>
                <p>只需发送邮件到 <strong>709703094@qq.com</strong>，在<strong>主题</strong>中输入指令即可！</p>
                
                <div class="tip">
                    💡 <strong>重要提示：</strong>指令需要以 <span class="command">#</span> 开头
                </div>
                
                <h3>📋 支持的指令</h3>
                <table>
                    <tr>
                        <th>指令</th>
                        <th>功能</th>
                        <th>示例</th>
                    </tr>
                    <tr>
                        <td><span class="command">#帮助</span></td>
                        <td>查看所有指令</td>
                        <td>主题：#帮助</td>
                    </tr>
                    <tr>
                        <td><span class="command">#股票</span></td>
                        <td>查看关注股票</td>
                        <td>主题：#股票</td>
                    </tr>
                    <tr>
                        <td><span class="command">#日报</span></td>
                        <td>获取今日日报</td>
                        <td>主题：#日报</td>
                    </tr>
                    <tr>
                        <td><span class="command">#状态</span></td>
                        <td>系统运行状态</td>
                        <td>主题：#状态</td>
                    </tr>
                    <tr>
                        <td><span class="command">#搜索</span></td>
                        <td>搜索市场信息</td>
                        <td>主题：#搜索 蓝牙耳机</td>
                    </tr>
                    <tr>
                        <td><span class="command">#推送</span></td>
                        <td>推送到企业微信</td>
                        <td>主题：#推送</td>
                    </tr>
                </table>
                
                <h3>🚀 立即试试</h3>
                <div class="command-box">
                    <p><strong>新建一封邮件：</strong></p>
                    <p>收件人：<span class="command">709703094@qq.com</span></p>
                    <p>主题：<span class="command">#帮助</span></p>
                    <p>正文：(可以不填)</p>
                    <p>然后点击发送！系统会在1分钟内回复你 📬</p>
                </div>
                
                <h3>⏰ 响应时间</h3>
                <p>系统每 <strong>60秒</strong> 检查一次邮箱，收到指令后会立即处理并回复。</p>
                
            </div>
            
            <div class="footer">
                <p>🤖 一人公司AI系统</p>
                <p>⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>💚 系统运行正常</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    # 发送
    try:
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(username, auth_code)
            server.sendmail(username, [username], msg.as_string())
        print("✅ 欢迎邮件已发送！请查看邮箱")
        return True
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

if __name__ == "__main__":
    send_welcome_email()
