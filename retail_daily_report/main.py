# -*- coding: utf-8 -*-
"""
零售日报系统 - 主程序入口
每日早8点自动推送零售行业最新动态（邮箱+企微双通道）
"""
import sys
import os
import json
from pathlib import Path
from datetime import datetime, timedelta

# 确保项目根目录在路径中
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# 推送记录文件
PUSH_LOG_FILE = PROJECT_ROOT / "data" / "push_log.json"


def load_push_log() -> dict:
    """加载推送记录"""
    if PUSH_LOG_FILE.exists():
        try:
            with open(PUSH_LOG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"records": []}


def save_push_log(log: dict):
    """保存推送记录"""
    PUSH_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PUSH_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


def record_push(success: bool, email_ok: bool, wecom_ok: bool, news_count: int, error: str = None):
    """记录推送结果"""
    log = load_push_log()
    record = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "success": success,
        "email_ok": email_ok,
        "wecom_ok": wecom_ok,
        "news_count": news_count,
        "error": error
    }
    log["records"].append(record)
    # 只保留最近30天的记录
    log["records"] = log["records"][-30:]
    save_push_log(log)


def check_yesterday_push() -> tuple:
    """
    检查昨天是否成功推送
    
    Returns:
        (是否需要告警, 告警信息)
    """
    log = load_push_log()
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    yesterday_records = [r for r in log.get("records", []) if r.get("date") == yesterday]
    
    if not yesterday_records:
        return True, f"昨日({yesterday})未找到推送记录，可能系统未运行"
    
    # 检查是否有成功的推送
    success_records = [r for r in yesterday_records if r.get("success")]
    if not success_records:
        errors = [r.get("error", "未知错误") for r in yesterday_records if r.get("error")]
        return True, f"昨日({yesterday})推送全部失败，错误: {'; '.join(errors)}"
    
    return False, None


def send_self_check_alert(alert_message: str):
    """发送自检告警"""
    from utils.email_sender import EmailSender
    from utils.wecom_sender import WeComSender
    
    # 发送邮件告警
    email_sender = EmailSender()
    alert_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; }}
            .alert {{ background: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 10px; }}
            .title {{ color: #856404; font-size: 20px; font-weight: bold; }}
            .solution {{ background: #e8f5e9; padding: 15px; border-radius: 8px; margin-top: 15px; }}
            code {{ background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }}
        </style>
    </head>
    <body>
        <div class="alert">
            <div class="title">⚠️ 零售日报系统自检告警</div>
            <p><strong>问题描述：</strong>{alert_message}</p>
            <p><strong>检测时间：</strong>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        <div class="solution">
            <h3>🔧 可能的解决方案：</h3>
            <ol>
                <li><strong>GitHub Actions 未运行</strong>：检查仓库 Actions 页面是否有报错</li>
                <li><strong>API Key 失效</strong>：检查 Brave Search API Key 是否有效</li>
                <li><strong>邮箱授权码过期</strong>：重新生成QQ邮箱授权码并更新 GitHub Secrets</li>
                <li><strong>网络问题</strong>：检查 GitHub Actions 运行日志</li>
            </ol>
            <p>查看运行日志：<a href="https://github.com/popeyeluo-coder/personal-assistant/actions">GitHub Actions</a></p>
        </div>
    </body>
    </html>
    """
    email_sender._send_email(alert_html, f"【零售日报告警】系统自检发现问题 - {datetime.now().strftime('%Y-%m-%d')}")
    
    # 发送企微告警
    wecom_sender = WeComSender()
    wecom_sender.send_alert("零售日报系统自检告警", alert_message + "\n\n请检查 GitHub Actions 运行日志")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🛒 零售日报系统启动")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    email_ok = False
    wecom_ok = False
    news_count = 0
    error_msg = None
    
    try:
        # 1. 数据采集
        print("\n📡 步骤1: 数据采集")
        from collectors.data_collector import collect_retail_news
        collected_data = collect_retail_news()
        
        if not collected_data:
            error_msg = "未采集到数据"
            print(f"⚠️ {error_msg}，跳过后续步骤")
            record_push(False, False, False, 0, error_msg)
            return
        
        news_count = len(collected_data)
        
        # 2. 数据分析
        print("\n📊 步骤2: 数据分析")
        from analyzers.data_analyzer import analyze_retail_news
        analysis_results = analyze_retail_news(collected_data)
        
        # 3. 生成报告
        print("\n📝 步骤3: 生成报告")
        from reports.report_generator import generate_retail_report
        html_report = generate_retail_report(analysis_results)
        
        # 4. 发送邮件
        print("\n📧 步骤4: 发送邮件")
        from utils.email_sender import send_report
        today_str = datetime.now().strftime("%Y年%m月%d日")
        email_ok = send_report(html_report, today_str)
        
        # 5. 发送企微
        print("\n💬 步骤5: 推送企微")
        from utils.wecom_sender import send_wecom_report
        
        # 直接传递完整的分析结果给企微（新版）
        wecom_ok = send_wecom_report(analysis_results, today_str)
        
        # 记录推送结果
        success = email_ok or wecom_ok
        record_push(success, email_ok, wecom_ok, news_count, None if success else "推送失败")
        
        if email_ok and wecom_ok:
            print("\n" + "="*60)
            print("✅ 零售日报生成并发送成功！（邮箱+企微）")
            print("="*60)
        elif email_ok:
            print("\n⚠️ 报告已发送邮箱，但企微推送失败")
        elif wecom_ok:
            print("\n⚠️ 报告已推送企微，但邮件发送失败")
        else:
            print("\n❌ 邮箱和企微推送均失败")
            
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
        record_push(False, False, False, news_count, error_msg)
        raise


def self_check():
    """每日自检"""
    print("\n🔍 执行每日自检...")
    need_alert, alert_msg = check_yesterday_push()
    
    if need_alert:
        print(f"⚠️ 发现问题: {alert_msg}")
        send_self_check_alert(alert_msg)
    else:
        print("✅ 昨日推送正常")


if __name__ == "__main__":
    # 支持命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # 测试模式：只采集不发送
            print("🧪 测试模式")
            from collectors.data_collector import collect_retail_news
            news = collect_retail_news()
            print(f"\n采集到 {len(news)} 条新闻")
            for i, item in enumerate(news[:5], 1):
                print(f"{i}. {item.get('title', '')[:50]}")
        elif sys.argv[1] == "--run-now":
            main()
        elif sys.argv[1] == "--self-check":
            self_check()
        elif sys.argv[1] == "--send-now":
            # 立即发送（用于补发）
            main()
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("用法: python main.py [--test|--run-now|--self-check|--send-now]")
    else:
        main()
