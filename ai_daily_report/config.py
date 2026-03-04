# -*- coding: utf-8 -*-
"""
AI日报系统 - 配置文件
每天早上8:00自动推送AI领域最新动态
"""
import os

# ==================== 搜索API配置 ====================
BRAVE_SEARCH_CONFIG = {
    "api_key": os.environ.get("BRAVE_API_KEY", "BSA2f0EsW7yU8canxgUOnfwYvhlUY1L"),
    "base_url": "https://api.search.brave.com/res/v1/web/search",
    "results_per_query": 15,
    "freshness": "pd",  # 过去24小时
}

# ==================== 邮件配置 ====================
_receiver_emails_str = os.environ.get("RECEIVER_EMAILS", "709703094@qq.com")
_receiver_emails = [email.strip() for email in _receiver_emails_str.split(",") if email.strip()]

EMAIL_CONFIG = {
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender_email": os.environ.get("SENDER_EMAIL", "709703094@qq.com"),
    "sender_password": os.environ.get("EMAIL_PASSWORD", ""),
    "receiver_emails": _receiver_emails,
    "subject_template": "【AI日报】{date} | 人工智能领域最新动态",
}

# ==================== 定时任务配置 ====================
SCHEDULE_CONFIG = {
    "send_time": "08:00",
    "send_days": "daily",  # 每天发送
    "timezone": "Asia/Shanghai",
    "report_type": "daily",
}

# ==================== 爬虫配置 ====================
CRAWLER_CONFIG = {
    "headers": {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    },
    "timeout": 30,
    "request_interval": 1.0,
    "max_retries": 3,
}

# ==================== AI日报关键词配置 ====================
KEYWORDS = {
    # 核心关键词（每次必搜）
    "primary": [
        "ChatGPT",
        "Claude",
        "GPT-5",
        "Gemini",
        "人工智能 突破",
        "AI Agent",
        "大模型 发布",
    ],
    
    # 大模型厂商
    "llm_vendors": [
        "OpenAI",
        "Anthropic Claude",
        "Google DeepMind",
        "Meta AI Llama",
        "Mistral AI",
        "字节跳动 豆包",
        "阿里 通义千问",
        "百度 文心一言",
        "腾讯 混元",
        "智谱 GLM",
        "月之暗面 Kimi",
        "MiniMax",
        "零一万物",
    ],
    
    # AI应用领域
    "applications": [
        "AI编程 Copilot",
        "AI绘画 Midjourney",
        "AI视频 Sora",
        "AI音乐 Suno",
        "AI搜索 Perplexity",
        "AI写作",
        "AI客服",
        "AI医疗",
        "AI教育",
        "AI金融",
        "自动驾驶 AI",
    ],
    
    # 技术突破
    "technology": [
        "多模态大模型",
        "AI推理能力",
        "AI安全",
        "AI对齐",
        "RAG 检索增强",
        "AI芯片",
        "NVIDIA AI",
        "AI算力",
        "开源大模型",
    ],
    
    # 行业动态
    "industry": [
        "AI融资",
        "AI独角兽",
        "AI收购",
        "AI政策 监管",
        "AI人才",
        "AGI 通用人工智能",
    ],
}

# ==================== AI相关性过滤规则 ====================
AI_FILTER = {
    # 必须包含的词（至少一个）
    "must_include": [
        "AI", "人工智能", "大模型", "LLM", "GPT", "Claude", "Gemini",
        "机器学习", "深度学习", "神经网络", "自然语言处理", "NLP",
        "生成式AI", "AIGC", "智能", "算法", "模型",
    ],
    
    # 必须排除的词
    "must_exclude": [
        "AI换脸诈骗", "AI诈骗", "赌博", "色情",
    ],
    
    # 相关性加分词
    "relevance_boost": [
        "突破", "发布", "开源", "融资", "收购", "合作",
        "首次", "最新", "重磅", "独家", "官宣",
        "性能提升", "超越", "领先", "创新",
    ],
    
    # 高价值来源
    "trusted_sources": [
        "36kr", "36氪", "机器之心", "量子位", "新智元",
        "雷峰网", "极客公园", "虎嗅", "钛媒体",
        "OpenAI", "Anthropic", "Google AI", "Meta AI",
        "腾讯科技", "网易科技", "新浪科技",
    ],
}

# ==================== 重点关注对象 ====================
KEY_COMPANIES = {
    # 国际AI巨头
    "international": [
        "OpenAI", "Anthropic", "Google DeepMind", "Meta AI",
        "Microsoft", "Amazon", "Apple", "NVIDIA",
        "Mistral", "Cohere", "Stability AI", "Midjourney",
    ],
    
    # 国内AI公司
    "domestic": [
        "百度", "阿里", "腾讯", "字节跳动", "华为",
        "智谱AI", "月之暗面", "MiniMax", "百川智能",
        "零一万物", "昆仑万维", "商汤", "科大讯飞",
        "Face++", "第四范式", "云从科技",
    ],
    
    # AI应用公司
    "applications": [
        "Notion AI", "Jasper", "Copy.ai", "Runway",
        "Character.AI", "Inflection", "Adept", "Covariant",
    ],
}

# ==================== 维度体系 ====================
DIMENSION_SYSTEM = {
    # 技术突破维度
    "tech_breakthrough": {
        "name": "技术突破",
        "icon": "🔬",
        "keywords": ["突破", "创新", "首次", "领先", "超越", "性能", "benchmark"],
        "priority_boost": 20,
    },
    
    # 产品发布维度
    "product_launch": {
        "name": "产品发布",
        "icon": "🚀",
        "keywords": ["发布", "上线", "推出", "开放", "beta", "preview"],
        "priority_boost": 15,
    },
    
    # 商业动态维度
    "business": {
        "name": "商业动态",
        "icon": "💼",
        "keywords": ["融资", "收购", "合作", "估值", "IPO", "投资"],
        "priority_boost": 12,
    },
    
    # 开源生态维度
    "opensource": {
        "name": "开源生态",
        "icon": "📦",
        "keywords": ["开源", "GitHub", "开放", "社区", "贡献"],
        "priority_boost": 10,
    },
    
    # 政策监管维度
    "policy": {
        "name": "政策监管",
        "icon": "📜",
        "keywords": ["监管", "政策", "法规", "合规", "安全", "审查"],
        "priority_boost": 15,
    },
    
    # 应用落地维度
    "application": {
        "name": "应用落地",
        "icon": "🎯",
        "keywords": ["应用", "落地", "场景", "案例", "部署", "实践"],
        "priority_boost": 8,
    },
    
    # 行业观点维度
    "opinion": {
        "name": "行业观点",
        "icon": "💬",
        "keywords": ["观点", "评论", "分析", "预测", "趋势"],
        "priority_boost": 5,
    },
}

# ==================== 存储配置 ====================
STORAGE_CONFIG = {
    "data_dir": "data",
    "report_dir": "reports",
    "cache_dir": "cache",
    "log_dir": "logs",
    "retention_days": 30,
}

# ==================== 日志配置 ====================
LOG_CONFIG = {
    "level": "INFO",
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    "rotation": "1 day",
    "retention": "7 days",
}
