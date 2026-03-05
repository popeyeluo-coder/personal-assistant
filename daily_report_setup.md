# 日报系统定时任务配置说明

## 问题描述
2026年3月5日，日报没有按时推送给用户。

## 根本原因
1. **GitHub Actions定时配置错误**：配置的是北京时间每天8:00推送（UTC 0:00），但用户期望的是18:00推送
2. **本地缺少定时任务备份**：AI日报和零售日报都没有配置本地的launchd定时任务

## 已完成的修复

### 1. GitHub Actions配置修改
- **AI日报**：
  - 推送时间：从北京时间8:00改为18:00（UTC 10:00）
  - 自检时间：从北京时间8:30改为18:30（UTC 10:30）
- **零售日报**：
  - 推送时间：从北京时间8:00改为18:00（UTC 10:05）
  - 自检时间：从北京时间8:30改为18:30（UTC 10:35）

### 2. 本地定时任务创建
创建了两个launchd定时任务作为GitHub Actions的备份保障：

#### AI日报定时任务
- **配置文件**：`~/Library/LaunchAgents/com.popeye.ai-daily-report.plist`
- **推送时间**：每天北京时间18:00
- **执行命令**：`/Users/popeye/Desktop/Codebuddy/【0】个人助理/ai_daily_report/run_report.py`
- **日志文件**：
  - 标准输出：`logs/launchd_stdout.log`
  - 标准错误：`logs/launchd_stderr.log`

#### 零售日报定时任务
- **配置文件**：`~/Library/LaunchAgents/com.popeye.retail-daily-report.plist`
- **推送时间**：每天北京时间18:05
- **执行命令**：`/Users/popeye/Desktop/Codebuddy/【0】个人助理/retail_daily_report/run_report.py`
- **日志文件**：
  - 标准输出：`logs/launchd_stdout.log`
  - 标准错误：`logs/launchd_stderr.log`

### 3. 包装脚本创建
为了确保定时任务能够正确运行，创建了包装脚本：
- `ai_daily_report/run_report.py` - AI日报包装脚本
- `retail_daily_report/run_report.py` - 零售日报包装脚本

这些脚本会自动切换到正确的目录并设置Python路径，然后运行主程序。

## 双重保障机制

现在日报系统具有双重保障：

### 主推送通道：GitHub Actions
- 每天北京时间18:00自动运行
- 运行环境：Ubuntu服务器
- 优势：即使本地电脑关机也能推送
- 支持失败重试和告警

### 备份推送通道：本地launchd
- 每天北京时间18:00/18:05自动运行
- 运行环境：本地Mac电脑
- 优势：如果GitHub Actions失败，本地会自动推送
- 日志记录在本地，方便排查问题

## 验证方法

### 检查定时任务状态
```bash
# 查看所有定时任务
launchctl list | grep -E "ai-daily-report|retail-daily-report"

# 查看AI日报配置
plutil -p ~/Library/LaunchAgents/com.popeye.ai-daily-report.plist

# 查看零售日报配置
plutil -p ~/Library/LaunchAgents/com.popeye.retail-daily-report.plist
```

### 手动测试
```bash
# 测试AI日报
cd /Users/popeye/Desktop/Codebuddy/【0】个人助理/ai_daily_report
python3 run_report.py

# 测试零售日报
cd /Users/popeye/Desktop/Codebuddy/【0】个人助理/retail_daily_report
python3 run_report.py
```

### 查看日志
```bash
# AI日报日志
tail -f /Users/popeye/Desktop/Codebuddy/【0】个人助理/ai_daily_report/logs/launchd_stdout.log

# 零售日报日志
tail -f /Users/popeye/Desktop/Codebuddy/【0】个人助理/retail_daily_report/logs/launchd_stdout.log
```

## 管理定时任务

### 停用定时任务
```bash
launchctl unload ~/Library/LaunchAgents/com.popeye.ai-daily-report.plist
launchctl unload ~/Library/LaunchAgents/com.popeye.retail-daily-report.plist
```

### 启用定时任务
```bash
launchctl load ~/Library/LaunchAgents/com.popeye.ai-daily-report.plist
launchctl load ~/Library/LaunchAgents/com.popeye.retail-daily-report.plist
```

### 编辑定时任务
```bash
# 编辑配置文件后需要重新加载
plutil -p ~/Library/LaunchAgents/com.popeye.ai-daily-report.plist
launchctl unload ~/Library/LaunchAgents/com.popeye.ai-daily-report.plist
launchctl load ~/Library/LaunchAgents/com.popeye.ai-daily-report.plist
```

## 注意事项

1. **本地Python环境**：确保Python3和所有依赖已正确安装
2. **网络连接**：本地推送需要网络连接才能访问Brave Search API和发送邮件
3. **电脑开机**：本地定时任务需要电脑开机且用户已登录才能运行
4. **时区设置**：定时任务使用系统时区，确保时区设置正确（北京时间 = UTC+8）

## 修复时间
2026年3月5日 18:20

## 修复结果
✅ GitHub Actions配置已更新并推送
✅ 本地定时任务已创建并加载
✅ 今天的日报已成功发送
✅ 双重保障机制已建立
