#!/usr/bin/env python3
"""
专家级日报推送脚本
- 多轮搜索 + 严格筛选 + AI深度分析
- 每条新闻配专业小结（启示+微信支付结合点）
- 确保内容专业度和价值度
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
from services.expert_report_service import ExpertReportService

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
    import requests
    
    webhook_url = config.get('notification', {}).get('wechat_bot', {}).get('webhook_url', '')
    if not webhook_url:
        logger.warning("未配置企微Webhook")
        return False
    
    try:
        # 企微Markdown限制4096字符
        if len(content) > 4000:
            content = content[:4000] + "\n\n...(更多内容见邮件)"
        
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        response = requests.post(webhook_url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("errcode") == 0:
                logger.info("✅ 企微推送成功")
                return True
            else:
                logger.error(f"❌ 企微推送失败: {result.get('errmsg')}")
                return False
        else:
            logger.error(f"❌ 企微请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 企微推送异常: {e}")
        return False


def run_expert_daily_report():
    """
    执行专家级日报推送
    """
    logger.info("=" * 70)
    logger.info("📰 开始生成专家级日报 - 确保内容高质量")
    logger.info("=" * 70)
    
    config = load_config()
    brave_key = config.get("search", {}).get("brave", {}).get("api_key", "")
    email_username = config.get('notification', {}).get('email', {}).get('username', '')
    
    # 初始化专家级报告服务
    report_service = ExpertReportService({"brave_api_key": brave_key})
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # ========== 1. 生成并推送AI日报 ==========
    logger.info("\n🤖 生成AI前沿日报（专家版）...")
    try:
        ai_report = report_service.generate_ai_daily_report()
        
        if ai_report.get('total_news', 0) > 0:
            # 企微推送（精简Markdown）
            ai_md = report_service.format_ai_report_markdown(ai_report)
            send_wechat(ai_md, config)
            
            # 邮件推送（完整HTML）
            ai_html = report_service.format_ai_report_html(ai_report)
            send_email(
                to=email_username,
                subject=f"🤖 AI前沿日报（专家版）- {date_str}",
                html_content=ai_html,
                config=config
            )
            
            logger.info(f"✅ AI日报推送完成，精选{ai_report.get('total_news', 0)}条高价值新闻")
        else:
            logger.warning("⚠️ AI日报: 未找到符合质量标准的新闻")
        
    except Exception as e:
        logger.error(f"❌ AI日报生成失败: {e}")
        import traceback
        traceback.print_exc()
    
    # ========== 2. 生成并推送零售日报 ==========
    logger.info("\n🛒 生成零售行业日报（专家版）...")
    try:
        retail_report = report_service.generate_retail_daily_report()
        
        if retail_report.get('total_news', 0) > 0:
            # 企微推送
            retail_md = report_service.format_retail_report_markdown(retail_report)
            send_wechat(retail_md, config)
            
            # 邮件推送
            retail_html = report_service.format_retail_report_html(retail_report)
            send_email(
                to=email_username,
                subject=f"🛒 零售行业日报（专家版）- {date_str}",
                html_content=retail_html,
                config=config
            )
            
            logger.info(f"✅ 零售日报推送完成，精选{retail_report.get('total_news', 0)}条高价值新闻")
            logger.info(f"   微信支付机会: {len(retail_report.get('wechat_pay_opportunities', []))}个")
        else:
            logger.warning("⚠️ 零售日报: 未找到符合质量标准的新闻")
        
    except Exception as e:
        logger.error(f"❌ 零售日报生成失败: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("\n" + "=" * 70)
    logger.info("📰 专家级日报推送完成")
    logger.info("=" * 70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='专家级日报推送')
    parser.add_argument('--run', action='store_true', help='立即执行推送')
    parser.add_argument('--ai-only', action='store_true', help='仅推送AI日报')
    parser.add_argument('--retail-only', action='store_true', help='仅推送零售日报')
    
    args = parser.parse_args()
    
    if args.ai_only:
        logger.info("仅推送AI日报...")
        config = load_config()
        brave_key = config.get("search", {}).get("brave", {}).get("api_key", "")
        email_username = config.get('notification', {}).get('email', {}).get('username', '')
        
        report_service = ExpertReportService({"brave_api_key": brave_key})
        ai_report = report_service.generate_ai_daily_report()
        
        if ai_report.get('total_news', 0) > 0:
            ai_md = report_service.format_ai_report_markdown(ai_report)
            send_wechat(ai_md, config)
            
            ai_html = report_service.format_ai_report_html(ai_report)
            date_str = datetime.now().strftime("%Y-%m-%d")
            send_email(
                to=email_username,
                subject=f"🤖 AI前沿日报（专家版）- {date_str}",
                html_content=ai_html,
                config=config
            )
            logger.info(f"✅ AI日报推送完成")
    
    elif args.retail_only:
        logger.info("仅推送零售日报...")
        config = load_config()
        brave_key = config.get("search", {}).get("brave", {}).get("api_key", "")
        email_username = config.get('notification', {}).get('email', {}).get('username', '')
        
        report_service = ExpertReportService({"brave_api_key": brave_key})
        retail_report = report_service.generate_retail_daily_report()
        
        if retail_report.get('total_news', 0) > 0:
            retail_md = report_service.format_retail_report_markdown(retail_report)
            send_wechat(retail_md, config)
            
            retail_html = report_service.format_retail_report_html(retail_report)
            date_str = datetime.now().strftime("%Y-%m-%d")
            send_email(
                to=email_username,
                subject=f"🛒 零售行业日报（专家版）- {date_str}",
                html_content=retail_html,
                config=config
            )
            logger.info(f"✅ 零售日报推送完成")
    
    else:
        run_expert_daily_report()
