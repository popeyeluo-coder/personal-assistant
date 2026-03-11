# 专家Skill 分发指南

## 📦 概述

本文档说明如何将 AI专家日报 Skill (ai-expert-daily-report) 和移动支付专家 Skill (mobile-payment-expert) 分发到其他环境或项目。

## 🗂️ Skill 文件结构

### AI专家日报 Skill
```
ai-expert-daily-report/
├── SKILL.md                          # Skill核心配置和使用指南
├── config/
│   └── skill_config.json            # Skill配置和偏好设置
├── references/
│   ├── ai_technologies.md           # AI技术参考文档
│   ├── ai_companies.md              # AI公司参考文档
│   └── api_reference.md            # API参考文档
├── scripts/
│   ├── skill_optimizer.py           # 自我优化脚本
│   └── example.py                  # 示例脚本
└── assets/
    └── example_asset.txt          # 示例资源文件
```

### 移动支付专家 Skill
```
mobile-payment-expert/
├── SKILL.md                          # Skill核心配置和使用指南
├── config/
│   └── skill_config.json            # Skill配置和偏好设置
├── references/
│   ├── wechat_pay.md                # 微信支付参考文档
│   ├── alipay.md                    # 支付宝参考文档（含碰一下）
│   └── api_reference.md            # API参考文档
├── scripts/
│   ├── skill_optimizer.py           # 自我优化脚本
│   └── example.py                  # 示例脚本
└── assets/
    └── example_asset.txt          # 示例资源文件
```

## 📦 分发方式

### 方式1: 完整目录分发

将整个 skill 目录复制到目标环境：

```bash
# 复制AI专家Skill
cp -r ai-expert-daily-report/ /path/to/target/skills/

# 复制移动支付专家Skill
cp -r mobile-payment-expert/ /path/to/target/skills/
```

### 方式2: GitHub 仓库分发

1. 将 skill 推送到 GitHub 仓库
2. 其他用户通过 git clone 获取

```bash
# 克隆仓库
git clone https://github.com/popeyeluo-coder/personal-assistant.git

# skill 位于 skills/ 目录下
cd personal-assistant/skills/
```

### 方式3: 压缩包分发

```bash
# 创建压缩包
zip -r ai-expert-daily-report-v2.0.zip ai-expert-daily-report/
zip -r mobile-payment-expert-v2.0.zip mobile-payment-expert/

# 分发压缩包
```

## 🔧 安装步骤

### 步骤1: 复制 Skill 文件

```bash
# 假设目标项目的 skills 目录为 /path/to/project/skills/
cp -r ai-expert-daily-report/ /path/to/project/skills/
cp -r mobile-payment-expert/ /path/to/project/skills/
```

### 步骤2: 配置 Skill 参数

编辑每个 skill 的配置文件：

```bash
# 编辑AI专家Skill配置
vim /path/to/project/skills/ai-expert-daily-report/config/skill_config.json

# 编辑移动支付专家Skill配置
vim /path/to/project/skills/mobile-payment-expert/config/skill_config.json
```

**关键配置项**:

```json
{
  "version": "2.0.0",
  "last_updated": "2026-03-06",
  "skill_name": "ai-expert-daily-report",
  "user_preferences": {
    "time_filter_days": 3,        // 新闻时效性过滤天数
    "structured_output": true,     // 是否启用结构化输出
    "entrepreneurial_insights": true // 是否启用创业建议
  }
}
```

### 步骤3: 安装依赖

```bash
# 确保安装了必要的 Python 依赖
pip3 install requests beautifulsoup4 lxml python-dateutil
```

### 步骤4: 测试 Skill

```bash
cd /path/to/project/skills/ai-expert-daily-report
python3 scripts/example.py

cd /path/to/project/skills/mobile-payment-expert
python3 scripts/example.py
```

## 🚀 快速开始模板

### Python 项目中使用

```python
from pathlib import Path

# 导入 skill 配置
skill_root = Path("/path/to/skills/ai-expert-daily-report")
config_path = skill_root / "config" / "skill_config.json"

import json
with open(config_path) as f:
    skill_config = json.load(f)

# 使用 skill 配置
print(f"Skill version: {skill_config['version']}")
print(f"Time filter: {skill_config['user_preferences']['time_filter_days']} days")
```

### 集成到日报系统

```python
import sys
from pathlib import Path

# 添加 skill 到路径
skill_root = Path("/path/to/skills/ai-expert-daily-report")
sys.path.insert(0, str(skill_root))

# 导入 skill 模块
from scripts.skill_optimizer import SkillOptimizer

# 使用 skill
optimizer = SkillOptimizer(skill_root)
optimizer.optimize_keywords()
```

## ⚙️ 自定义配置

### 修改新闻时效性

```json
{
  "user_preferences": {
    "time_filter_days": 7  // 改为7天
  }
}
```

### 关闭创业建议

```json
{
  "user_preferences": {
    "entrepreneurial_insights": false  // 关闭创业建议
  }
}
```

### 修改关注领域

```json
{
  "user_preferences": {
    "focus_areas": [
      "自定义领域1",
      "自定义领域2"
    ]
  }
}
```

## 🔄 更新 Skill

### 检查更新

```bash
# 查看当前版本
cat skills/ai-expert-daily-report/config/skill_config.json | grep version
cat skills/mobile-payment-expert/config/skill_config.json | grep version
```

### 更新步骤

1. 备份当前配置
```bash
cp skills/ai-expert-daily-report/config/skill_config.json /tmp/backup.json
```

2. 复制新版本
```bash
cp -r new-ai-expert-daily-report/* skills/ai-expert-daily-report/
```

3. 恢复配置
```bash
cp /tmp/backup.json skills/ai-expert-daily-report/config/skill_config.json
```

4. 测试新版本
```bash
cd skills/ai-expert-daily-report
python3 scripts/example.py
```

## 📊 版本兼容性

### v2.0.0 (2026-03-06)

**新特性**:
- ✅ 严格3天时效性过滤
- ✅ 结构化输出
- ✅ 分类小结
- ✅ 创业建议

**兼容性**: 完全兼容 v1.0.0 配置

### v1.0.0 (2026-03-05)

**基础特性**:
- 基础行业报告
- 自我迭代机制

## 🐛 常见问题

### Q1: 如何禁用时效性过滤？

A: 设置 `time_filter_days: 0` 或移除相关代码

### Q2: 如何修改输出格式？

A: 编辑 SKILL.md 中的报告结构部分

### Q3: 如何添加自定义关键词？

A: 编辑 config/skill_config.json 中的 search_keywords

### Q4: 如何集成到其他项目？

A: 参考"快速开始模板"部分

## 📞 支持与反馈

### 获取帮助
- 邮箱: 709703094@qq.com
- GitHub: https://github.com/popeyeluo-coder/personal-assistant

### 反馈问题
1. 邮件描述问题
2. 附上错误日志
3. 提供系统环境信息

## 📝 许可证

本 Skill 为开源项目，遵循 MIT 许可证。

---

**最后更新**: 2026-03-06  
**当前版本**: 2.0.0  
**作者**: popeyeluo-coder
