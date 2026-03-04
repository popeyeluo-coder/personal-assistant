#!/usr/bin/env python3
"""
专业日报推送脚本
每天8:00自动执行，推送AI日报和零售日报到企微和邮箱
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from services.professional_report_service import ProfessionalReportService
from services.mobile_service import MobileService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置路径
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config/api_keys.yaml")


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def send_email(to: str, subject: str, html_content: str, config: dict) -> bool:
    """发送HTML邮件"""
    email_config = config.get('notification', {}).get('email', {})
    username = email_config.get('username', '')
    auth_code = email_config.get('auth_code', '')
    
    try:
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(username, auth_code)
            server.sendmail(username, [to], msg.as_string())
        
        logger.info(f"✅ 邮件发送成功: {subject}")
        return True
    except Exception as e:
        logger.error(f"❌ 邮件发送失败: {e}")
        return False


def send_wechat(content: str, config: dict) -> bool:
    """发送企微消息"""
    webhook_url = config.get('notification', {}).get('wechat_bot', {}).get('webhook_url', '')
    if not webhook_url:
        logger.warning("未配置企微Webhook")
        return False
    
    service = MobileService({"wechat_webhook": webhook_url})
    result = service.send_wechat_markdown(content)
    
    if result.get("status") == "success":
        logger.info("✅ 企微推送成功")
        return True
    else:
        logger.error(f"❌ 企微推送失败: {result.get('message')}")
        return False


def run_professional_daily_report():
    """
    执行专业日报推送
    """
    logger.info("=" * 60)
    logger.info("📰 开始生成专业日报")
    logger.info("=" * 60)
    
    config = load_config()
    brave_key = config.get("search", {}).get("brave", {}).get("api_key", "")
    email_username = config.get('notification', {}).get('email', {}).get('username', '')
    
    # 初始化报告服务
    report_service = ProfessionalReportService({"brave_api_key": brave_key})
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # ========== 1. 生成并推送AI日报 ==========
    logger.info("\n🤖 生成AI前沿日报...")
    try:
        ai_report = report_service.generate_ai_report()
        
        # 企微推送（Markdown格式）
        ai_md = report_service.format_ai_report_markdown(ai_report)
        send_wechat(ai_md, config)
        
        # 邮件推送（HTML格式）
        ai_html = report_service.format_ai_report_html(ai_report)
        send_email(
            to=email_username,
            subject=f"🤖 AI前沿日报 - {date_str}",
            html_content=ai_html,
            config=config
        )
        
        logger.info(f"✅ AI日报推送完成，共{ai_report.get('total_news', 0)}条新闻")
        
    except Exception as e:
        logger.error(f"❌ AI日报生成失败: {e}")
    
    # ========== 2. 生成并推送零售日报 ==========
    logger.info("\n🛒 生成零售行业日报...")
    try:
        retail_report = report_service.generate_retail_report()
        
        # 企微推送
        retail_md = report_service.format_retail_report_markdown(retail_report)
        send_wechat(retail_md, config)
        
        # 邮件推送
        retail_html = report_service.format_retail_report_html(retail_report)
        send_email(
            to=email_username,
            subject=f"🛒 零售行业日报 - {date_str}",
            html_content=retail_html,
            config=config
        )
        
        domestic_count = sum(d.get('count', 0) for d in retail_report.get('domestic', {}).values())
        logger.info(f"✅ 零售日报推送完成，国内{domestic_count}条新闻")
        
    except Exception as e:
        logger.error(f"❌ 零售日报生成失败: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("📰 专业日报推送完成")
    logger.info("=" * 60)


def run_test():
    """测试推送（不实际抓取，使用模拟数据）"""
    logger.info("🧪 测试专业日报推送...")
    
    config = load_config()
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 测试消息
    test_ai_md = f"""# 🤖 AI前沿日报（测试）
> {date_str}

## ✅ 专业日报系统已配置

**推送时间**: 每天 08:00

**日报内容**:

### 1️⃣ AI前沿日报
- 🔧 硬件/芯片
- 🧠 大模型/基础模型
- ⚙️ 算法/技术
- 📱 应用/产品
- 🏢 产业/投资

### 2️⃣ 零售行业日报
- 🇨🇳 国内市场 (便利店/商超/商圈/免税/折扣)
- 🌍 海外市场
- 💳 微信支付机会洞察

---
*🧪 这是测试消息，确认系统配置正常*
*📰 明天8点将收到第一份正式日报*"""
    
    send_wechat(test_ai_md, config)
    
    email_username = config.get('notification', {}).get('email', {}).get('username', '')
    test_html = f"""
    <html>
    <body style="font-family: sans-serif; padding: 20px;">
        <h1>📰 专业日报系统已配置</h1>
        <p>推送时间: 每天 08:00</p>
        <hr>
        <h2>🤖 AI前沿日报</h2>
        <ul>
            <li>🔧 硬件/芯片</li>
            <li>🧠 大模型/基础模型</li>
            <li>⚙️ 算法/技术</li>
            <li>📱 应用/产品</li>
            <li>🏢 产业/投资</li>
        </ul>
        <h2>🛒 零售行业日报</h2>
        <ul>
            <li>🇨🇳 国内: 便利店/商超/商圈/免税/折扣</li>
            <li>🌍 海外市场动态</li>
            <li>💳 微信支付机会洞察</li>
        </ul>
        <hr>
        <p style="color: #999;">🧪 这是测试邮件 · {date_str}</p>
    </body>
    </html>
    """
    
    send_email(
        to=email_username,
        subject=f"📰 专业日报系统已配置 - {date_str}",
        html_content=test_html,
        config=config
    )
    
    logger.info("✅ 测试推送完成")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='专业日报推送')
    parser.add_argument('--test', action='store_true', help='测试模式')
    parser.add_argument('--run', action='store_true', help='立即执行推送')
    
    args = parser.parse_args()
    
    if args.test:
        run_test()
    elif args.run:
        run_professional_daily_report()
    else:
        # 默认测试
        run_test()
