#!/bin/bash
# 系统级 launchd 安装脚本

echo "=================================="
echo "安装系统级 launchd 定时任务"
echo "=================================="
echo ""

# 复制配置文件到 LaunchDaemons
echo "1. 复制配置文件..."
sudo cp "/Users/popeye/Desktop/Codebuddy/【0】个人助理/com.popeye.ai-daily-report.system.plist" /Library/LaunchDaemons/
sudo cp "/Users/popeye/Desktop/Codebuddy/【0】个人助理/com.popeye.retail-daily-report.system.plist" /Library/LaunchDaemons/

# 设置正确的权限
echo "2. 设置文件权限..."
sudo chmod 644 /Library/LaunchDaemons/com.popeye.ai-daily-report.system.plist
sudo chmod 644 /Library/LaunchDaemons/com.popeye.retail-daily-report.system.plist

# 创建日志目录（如果不存在）
echo "3. 创建日志目录..."
mkdir -p "/Users/popeye/Desktop/Codebuddy/【0】个人助理/ai_daily_report/logs"
mkdir -p "/Users/popeye/Desktop/Codebuddy/【0】个人助理/retail_daily_report/logs"

# 卸载旧的配置（如果存在）
echo "4. 卸载旧配置..."
sudo launchctl unload /Library/LaunchDaemons/com.popeye.ai-daily-report.system.plist 2>/dev/null || true
sudo launchctl unload /Library/LaunchDaemons/com.popeye.retail-daily-report.system.plist 2>/dev/null || true

# 加载新的配置
echo "5. 加载新配置..."
sudo launchctl load /Library/LaunchDaemons/com.popeye.ai-daily-report.system.plist
sudo launchctl load /Library/LaunchDaemons/com.popeye.retail-daily-report.system.plist

echo ""
echo "=================================="
echo "安装完成！"
echo "=================================="
echo ""
echo "系统级定时任务已配置，即使电脑关机后启动也会自动执行"
echo ""
echo "查看状态："
echo "  sudo launchctl list | grep com.popeye"
echo ""
echo "查看日志："
echo "  AI日报: /Users/popeye/Desktop/Codebuddy/【0】个人助理/ai_daily_report/logs/launchd_system_*.log"
echo "  零售日报: /Users/popeye/Desktop/Codebuddy/【0】个人助理/retail_daily_report/logs/launchd_system_*.log"
echo ""
echo "卸载配置（如需）："
echo "  sudo launchctl unload /Library/LaunchDaemons/com.popeye.ai-daily-report.system.plist"
echo "  sudo launchctl unload /Library/LaunchDaemons/com.popeye.retail-daily-report.system.plist"
echo ""
