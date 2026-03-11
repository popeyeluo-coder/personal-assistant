#!/bin/bash
# 系统级 launchd 卸载脚本

echo "=================================="
echo "卸载系统级 launchd 定时任务"
echo "=================================="
echo ""

# 卸载配置
echo "1. 卸载定时任务..."
sudo launchctl unload /Library/LaunchDaemons/com.popeye.ai-daily-report.system.plist 2>/dev/null || echo "AI日报定时任务未运行或已卸载"
sudo launchctl unload /Library/LaunchDaemons/com.popeye.retail-daily-report.system.plist 2>/dev/null || echo "零售日报定时任务未运行或已卸载"

# 删除配置文件
echo "2. 删除配置文件..."
sudo rm -f /Library/LaunchDaemons/com.popeye.ai-daily-report.system.plist
sudo rm -f /Library/LaunchDaemons/com.popeye.retail-daily-report.system.plist

echo ""
echo "=================================="
echo "卸载完成！"
echo "=================================="
echo ""
