#!/usr/bin/env python3
"""
测试企业微信机器人推送
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from services.mobile_service import MobileService

# 企业微信机器人配置
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=ed570230-8df9-4379-abf4-567ace0071de"

def main():
    print("=" * 50)
    print("📱 企业微信机器人测试")
    print("=" * 50)
    
    # 初始化服务
    service = MobileService({
        "wechat_webhook": WEBHOOK_URL
    })
    
    # 测试1: 发送普通文本
    print("\n🔄 测试1: 发送欢迎消息...")
    result1 = service.send_wechat_text(
        "🎉 恭喜！一人公司AI系统已成功连接你的手机！\n\n"
        "从现在开始，你可以在手机上实时接收：\n"
        "📊 每日运营日报\n"
        "📈 股票行情提醒\n"
        "🛒 爆品发现通知\n"
        "⚠️ 系统告警\n\n"
        f"⏰ 连接时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print(f"   结果: {result1}")
    
    # 测试2: 发送Markdown格式（更美观）
    print("\n🔄 测试2: 发送Markdown日报...")
    markdown_content = f"""# 🏢 一人公司日报
> {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

## 📊 系统状态
- 状态: <font color="info">✅ 正常运行</font>
- AI专家: 7人全员在岗
- 邮件服务: <font color="info">已配置</font>
- 企微推送: <font color="info">已连接</font>

## 📈 关注股票
1. 🟢 宏达股份 (600331)
2. 🟢 雅化集团 (002497)
3. 🟢 千里科技 (601777)
4. 🟢 中国软件国际 (00354)
5. 🟢 腾讯 (00700)

## 🤖 你的AI专家团队
| 角色 | 职能 |
|------|------|
| 📈 股票分析师 | 股票分析、趋势预测 |
| 🛒 电商专家 | 选品、市场分析 |
| 💰 财务顾问 | 成本核算、ROI分析 |
| 📝 内容创作者 | 文案、营销策划 |
| 🔧 技术顾问 | 产品开发、技术支持 |
| 📣 营销策略师 | 推广、渠道运营 |
| 🔍 市场调研员 | 市场调研、竞品分析 |

---
*一人公司 AI Agent System v1.0*
*📧 邮箱: 709703094@qq.com*"""

    result2 = service.send_wechat_markdown(markdown_content)
    print(f"   结果: {result2}")
    
    # 测试3: 发送股票告警示例
    print("\n🔄 测试3: 发送股票告警示例...")
    alert_content = """⚠️ **【股票异动提醒】**

**腾讯控股 (00700)**
- 当前价格: 388.60 港元
- 涨跌幅: <font color="info">+2.35%</font>
- 成交量: 较昨日增加 156%

**触发条件**: 涨幅超过2%

---
*此为演示消息，实际数据将在交易时段推送*"""

    result3 = service.send_wechat_markdown(alert_content)
    print(f"   结果: {result3}")
    
    print("\n" + "=" * 50)
    if all(r.get("status") == "success" for r in [result1, result2, result3]):
        print("🎉 全部测试通过！请检查企业微信群消息")
    else:
        print("⚠️ 部分测试失败，请检查错误信息")
    print("=" * 50)

if __name__ == "__main__":
    main()
