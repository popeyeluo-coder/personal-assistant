# -*- coding: utf-8 -*-
"""
AI日报系统 - 主程序入口
每日早8点自动推送AI领域最新动态
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# 确保项目根目录在路径中
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """主函数"""
    print("\n" + "="*60)
    print("🤖 AI日报系统启动")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        # 1. 数据采集
        print("\n📡 步骤1: 数据采集")
        from collectors.data_collector import collect_ai_news
        collected_data = collect_ai_news()
        
        if not collected_data:
            print("⚠️ 未采集到数据，跳过后续步骤")
            return
        
        # 2. 数据分析
        print("\n📊 步骤2: 数据分析")
        from analyzers.data_analyzer import analyze_ai_news
        analysis_results = analyze_ai_news(collected_data)
        
        # 3. 生成报告
        print("\n📝 步骤3: 生成报告")
        from reports.report_generator import generate_ai_report
        html_report = generate_ai_report(analysis_results)
        
        # 4. 发送邮件
        print("\n📧 步骤4: 发送邮件")
        from utils.email_sender import send_report
        today_str = datetime.now().strftime("%Y年%m月%d日")
        success = send_report(html_report, today_str)
        
        if success:
            print("\n" + "="*60)
            print("✅ AI日报生成并发送成功！")
            print("="*60)
        else:
            print("\n⚠️ 报告已生成，但邮件发送失败")
            print("   请检查邮箱配置或手动查看报告文件")
            
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # 支持命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # 测试模式：只采集不发送
            print("🧪 测试模式")
            from collectors.data_collector import collect_ai_news
            news = collect_ai_news()
            print(f"\n采集到 {len(news)} 条新闻")
            for i, item in enumerate(news[:5], 1):
                print(f"{i}. {item.get('title', '')[:50]}")
        elif sys.argv[1] == "--run-now":
            main()
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("用法: python main.py [--test|--run-now]")
    else:
        main()
