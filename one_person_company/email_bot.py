#!/usr/bin/env python3
"""
邮件机器人启动脚本
监听QQ邮箱，自动处理指令并回复
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml
import logging
import argparse
from services.email_bot_service import EmailBotService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), "config/api_keys.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description='📧 一人公司邮件机器人')
    parser.add_argument('--daemon', '-d', action='store_true', 
                        help='守护进程模式（持续运行）')
    parser.add_argument('--interval', '-i', type=int, default=30,
                        help='检查邮件间隔(秒)，默认30秒')
    parser.add_argument('--once', '-o', action='store_true',
                        help='只运行一次检查')
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config()
    email_config = config.get('notification', {}).get('email', {})
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║           📧 一人公司 - 邮件机器人服务                        ║
╠══════════════════════════════════════════════════════════════╣
║  监听邮箱: 709703094@qq.com                                  ║
║  指令前缀: # (井号)                                           ║
╠══════════════════════════════════════════════════════════════╣
║  📌 使用方法:                                                 ║
║  发送邮件到 709703094@qq.com                                 ║
║  主题格式: #指令 [参数]                                       ║
║                                                              ║
║  📋 支持的指令:                                               ║
║  • #帮助    - 查看所有指令                                    ║
║  • #股票    - 查看关注股票                                    ║
║  • #日报    - 获取运营日报                                    ║
║  • #状态    - 系统运行状态                                    ║
║  • #搜索 xx - 搜索市场信息                                    ║
║  • #推送    - 立即推送到企微                                  ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # 初始化机器人
    bot = EmailBotService({
        "username": email_config.get('username', ''),
        "auth_code": email_config.get('auth_code', ''),
    })
    
    if args.daemon:
        print(f"🚀 守护进程模式启动，检查间隔: {args.interval}秒")
        print("   按 Ctrl+C 停止\n")
        try:
            bot.run_daemon(args.interval)
        except KeyboardInterrupt:
            print("\n👋 邮件机器人已停止")
    elif args.once:
        print("🔍 检查一次邮箱...\n")
        count = bot.run_once()
        print(f"\n✅ 处理了 {count} 条指令")
    else:
        # 默认运行一次
        print("🔍 检查邮箱...\n")
        count = bot.run_once()
        print(f"\n✅ 处理了 {count} 条指令")
        print("\n💡 提示: 使用 --daemon 参数可持续监听邮箱")

if __name__ == "__main__":
    main()
