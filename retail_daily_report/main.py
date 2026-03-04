# -*- coding: utf-8 -*-
"""
零售日报系统 - 主程序入口
"""
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    print("\n" + "="*60)
    print("🛒 零售日报系统启动")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        print("\n📡 步骤1: 数据采集")
        from collectors.data_collector import collect_retail_news
        collected_data = collect_retail_news()
        
        if not collected_data:
            print("⚠️ 未采集到数据")
            return
        
        print("\n📊 步骤2: 数据分析")
        from analyzers.data_analyzer import analyze_retail_news
        analysis_results = analyze_retail_news(collected_data)
        
        print("\n📝 步骤3: 生成报告")
        from reports.report_generator import generate_retail_report
        html_report = generate_retail_report(analysis_results)
        
        print("\n📧 步骤4: 发送邮件")
        from utils.email_sender import send_report
        today_str = datetime.now().strftime("%Y年%m月%d日")
        success = send_report(html_report, today_str)
        
        if success:
            print("\n" + "="*60)
            print("✅ 零售日报生成并发送成功！")
            print("="*60)
        else:
            print("\n⚠️ 报告已生成，但邮件发送失败")
            
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            from collectors.data_collector import collect_retail_news
            news = collect_retail_news()
            print(f"\n采集到 {len(news)} 条新闻")
        elif sys.argv[1] == "--run-now":
            main()
    else:
        main()
