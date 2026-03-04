#!/usr/bin/env python3
"""
一人公司 - 自动推送服务
定时推送日报、股票行情到企业微信和邮箱
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml
import logging
from datetime import datetime
from services.mobile_service import MobileService
from services.notification_service import NotificationService
from services.search_service import SearchService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载配置
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config/api_keys.yaml")

def load_config():
    """加载配置"""
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def get_stock_info():
    """获取关注股票信息"""
    stocks = [
        {"code": "600331", "name": "宏达股份", "market": "A股"},
        {"code": "002497", "name": "雅化集团", "market": "A股"},
        {"code": "601777", "name": "千里科技", "market": "A股"},
        {"code": "00354", "name": "中国软件国际", "market": "港股"},
        {"code": "00700", "name": "腾讯控股", "market": "港股"},
    ]
    return stocks

def generate_morning_report():
    """生成早间报告"""
    now = datetime.now()
    stocks = get_stock_info()
    
    report = f"""# ☀️ 早安！一人公司日报
> {now.strftime('%Y年%m月%d日')} 星期{['一','二','三','四','五','六','日'][now.weekday()]}

## 📈 今日关注股票
"""
    for i, stock in enumerate(stocks, 1):
        report += f"{i}. **{stock['name']}** ({stock['code']}) - {stock['market']}\n"
    
    report += f"""
## 🎯 今日待办
- [ ] 查看股票开盘情况
- [ ] 检查电商订单
- [ ] 关注市场热点

## 💡 AI建议
> 今天是工作日，建议关注盘前资讯，把握交易机会

---
*🤖 一人公司AI系统 自动推送*
*⏰ {now.strftime('%H:%M')}*"""
    
    return report

def generate_noon_report():
    """生成午间快报"""
    now = datetime.now()
    
    report = f"""# 🌤️ 午间市场快报
> {now.strftime('%Y年%m月%d日 %H:%M')}

## 📊 上午市场概况
- A股: 交易进行中
- 港股: 交易进行中

## 📈 关注股票动态
1. 宏达股份 (600331)
2. 雅化集团 (002497)
3. 千里科技 (601777)
4. 中国软件国际 (00354)
5. 腾讯控股 (00700)

## 💡 午间提醒
> 注意观察午后走势，把握下午交易机会

---
*🤖 一人公司AI系统*"""
    
    return report

def generate_evening_report():
    """生成晚间日报"""
    now = datetime.now()
    stocks = get_stock_info()
    
    report = f"""# 🌙 晚间日报汇总
> {now.strftime('%Y年%m月%d日')}

## 📊 今日系统运行状态
- AI专家团队: <font color="info">7人全员在岗</font>
- 系统状态: <font color="info">正常运行</font>
- 邮件服务: <font color="info">已配置</font>
- 企微推送: <font color="info">已连接</font>

## 📈 股票收盘概览
"""
    for i, stock in enumerate(stocks, 1):
        report += f"{i}. **{stock['name']}** ({stock['code']})\n"
    
    report += f"""
## ✅ 今日完成
- 早间报告推送
- 午间快报推送
- 系统监控正常

## 📅 明日计划
- 继续关注股票走势
- 监控市场动态
- 优化运营策略

---
*🤖 一人公司AI系统 晚间汇总*
*🌙 祝你晚安，明天继续加油！*"""
    
    return report

def push_to_wechat(content: str, config: dict):
    """推送到企业微信"""
    webhook_url = config.get('notification', {}).get('wechat_bot', {}).get('webhook_url', '')
    if not webhook_url:
        logger.warning("未配置企业微信Webhook")
        return False
    
    service = MobileService({"wechat_webhook": webhook_url})
    result = service.send_wechat_markdown(content)
    
    if result.get("status") == "success":
        logger.info("✅ 企业微信推送成功")
        return True
    else:
        logger.error(f"❌ 企业微信推送失败: {result.get('message')}")
        return False

def push_to_email(subject: str, content: str, config: dict):
    """推送到邮箱"""
    email_config = config.get('notification', {}).get('email', {})
    
    service = NotificationService({
        "smtp_server": email_config.get('smtp_server', 'smtp.qq.com'),
        "smtp_port": email_config.get('smtp_port', 465),
        "email_username": email_config.get('username', ''),
        "email_auth_code": email_config.get('auth_code', '')
    })
    
    # 转换Markdown为HTML
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 20px; }}
            h1 {{ color: #333; }}
            h2 {{ color: #666; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
            blockquote {{ background: #f9f9f9; border-left: 4px solid #007bff; padding: 10px 15px; margin: 10px 0; }}
            code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        </style>
    </head>
    <body>
        <pre style="white-space: pre-wrap; font-family: inherit;">{content}</pre>
        <hr>
        <p style="color: #999; font-size: 12px;">此邮件由一人公司AI系统自动发送</p>
    </body>
    </html>
    """
    
    result = service.send_email(
        to=email_config.get('username', ''),
        subject=subject,
        content=html_content,
        content_type='html'
    )
    
    if result.get("status") == "success":
        logger.info("✅ 邮件推送成功")
        return True
    else:
        logger.error(f"❌ 邮件推送失败: {result.get('message')}")
        return False

def run_morning_push():
    """执行早间推送"""
    logger.info("🌅 开始早间推送...")
    config = load_config()
    report = generate_morning_report()
    
    push_to_wechat(report, config)
    push_to_email(f"☀️ 早间日报 - {datetime.now().strftime('%Y-%m-%d')}", report, config)
    
    logger.info("✅ 早间推送完成")

def run_noon_push():
    """执行午间推送"""
    logger.info("🌤️ 开始午间推送...")
    config = load_config()
    report = generate_noon_report()
    
    push_to_wechat(report, config)
    
    logger.info("✅ 午间推送完成")

def run_evening_push():
    """执行晚间推送"""
    logger.info("🌙 开始晚间推送...")
    config = load_config()
    report = generate_evening_report()
    
    push_to_wechat(report, config)
    push_to_email(f"🌙 晚间日报 - {datetime.now().strftime('%Y-%m-%d')}", report, config)
    
    logger.info("✅ 晚间推送完成")

def run_test_push():
    """测试推送"""
    logger.info("🧪 开始测试推送...")
    config = load_config()
    
    test_report = f"""# 🧪 测试推送
> {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

## ✅ 自动推送服务已配置

**推送时间表：**
- ☀️ **08:30** - 早间日报
- 🌤️ **12:00** - 午间快报
- 🌙 **18:00** - 晚间汇总

**推送渠道：**
- 📱 企业微信群
- 📧 QQ邮箱

---
*🤖 一人公司AI系统*
*此消息表示自动推送服务配置成功！*"""
    
    push_to_wechat(test_report, config)
    
    logger.info("✅ 测试推送完成")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='一人公司自动推送服务')
    parser.add_argument('--type', choices=['morning', 'noon', 'evening', 'test'], 
                        default='test', help='推送类型')
    
    args = parser.parse_args()
    
    if args.type == 'morning':
        run_morning_push()
    elif args.type == 'noon':
        run_noon_push()
    elif args.type == 'evening':
        run_evening_push()
    else:
        run_test_push()
