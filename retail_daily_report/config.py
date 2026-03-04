# -*- coding: utf-8 -*-
"""
零售日报系统 - 配置文件
每天早上8:00自动推送零售行业最新动态
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
    "subject_template": "【零售日报】{date} | 零售行业最新动态",
}

# ==================== 定时任务配置 ====================
SCHEDULE_CONFIG = {
    "send_time": "08:00",
    "send_days": "daily",
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

# ==================== 零售日报关键词配置 ====================
KEYWORDS = {
    # 核心关键词
    "primary": [
        "零售 新闻",
        "新零售",
        "消费 趋势",
        "零售业 动态",
        "商超 新闻",
        "便利店 行业",
    ],
    
    # 零售业态
    "retail_formats": [
        "便利店 7-11",
        "便利店 全家",
        "便利店 罗森",
        "超市 永辉",
        "超市 盒马",
        "超市 大润发",
        "仓储会员店 Costco",
        "仓储会员店 山姆",
        "折扣店 好特卖",
        "零食店 零食很忙",
        "社区团购",
        "即时零售",
    ],
    
    # 零售科技
    "retail_tech": [
        "无人零售",
        "智慧零售",
        "零售数字化",
        "零售AI",
        "智能货架",
        "自助结账",
        "RFID零售",
    ],
    
    # 消费趋势
    "consumer_trends": [
        "消费升级",
        "消费降级",
        "年轻人消费",
        "Z世代消费",
        "国潮消费",
        "绿色消费",
    ],
    
    # 零售巨头
    "retail_giants": [
        "阿里零售",
        "京东 实体店",
        "拼多多 线下",
        "美团 零售",
        "抖音 电商",
        "沃尔玛 中国",
    ],
    
    # 支付与营销
    "payment_marketing": [
        "微信支付 商户",
        "支付宝 零售",
        "数字人民币 零售",
        "零售 促销",
        "会员营销",
    ],
}

# ==================== 零售相关性过滤规则 ====================
RETAIL_FILTER = {
    # 必须包含的词（至少一个）
    "must_include": [
        "零售", "商超", "便利店", "超市", "门店", "店铺",
        "消费", "购物", "电商", "新零售", "实体店",
        "商品", "货架", "供应链", "仓储", "配送",
        "会员", "促销", "折扣", "支付",
    ],
    
    # 必须排除的词
    "must_exclude": [
        "赌博", "色情", "诈骗",
    ],
    
    # 相关性加分词
    "relevance_boost": [
        "开业", "关店", "扩张", "融资", "收购", "合作",
        "新品牌", "新业态", "首店", "旗舰店",
        "增长", "下滑", "转型", "升级",
    ],
    
    # 高价值来源
    "trusted_sources": [
        "36kr", "36氪", "联商网", "零售老板内参",
        "亿邦动力", "商业观察家", "灵兽传媒",
        "中国连锁经营协会", "零售圈",
        "虎嗅", "钛媒体", "界面新闻",
    ],
}

# ==================== 重点关注企业 ====================
KEY_COMPANIES = {
    # 便利店
    "convenience": [
        "7-11", "全家", "罗森", "便利蜂", "美宜佳",
        "Today便利店", "见福", "天福", "红旗连锁",
    ],
    
    # 超市/大卖场
    "supermarket": [
        "永辉", "盒马", "大润发", "沃尔玛", "家乐福",
        "华润万家", "物美", "联华", "步步高",
    ],
    
    # 会员店
    "membership": [
        "山姆", "Costco", "麦德龙", "盒马X会员店", "fudi",
    ],
    
    # 折扣店/零食店
    "discount": [
        "好特卖", "嗨特购", "奥特乐", "零食很忙",
        "赵一鸣零食", "糖巢", "零食优选",
    ],
    
    # 电商/新零售
    "ecommerce": [
        "阿里", "京东", "拼多多", "美团", "抖音",
        "叮咚买菜", "朴朴超市", "每日优鲜",
    ],
    
    # 国际品牌
    "international": [
        "Costco", "沃尔玛", "山姆", "ALDI", "Trader Joe's",
        "宜家", "优衣库", "无印良品", "名创优品",
    ],
}

# ==================== 维度体系 ====================
DIMENSION_SYSTEM = {
    # 开店/扩张
    "expansion": {
        "name": "开店扩张",
        "icon": "🏪",
        "keywords": ["开业", "开店", "新店", "首店", "扩张", "进驻", "入驻"],
        "priority_boost": 15,
    },
    
    # 闭店/收缩
    "contraction": {
        "name": "闭店收缩",
        "icon": "🚫",
        "keywords": ["关店", "闭店", "撤出", "退出", "收缩", "裁员"],
        "priority_boost": 18,
    },
    
    # 业态创新
    "innovation": {
        "name": "业态创新",
        "icon": "💡",
        "keywords": ["新业态", "创新", "升级", "转型", "新模式", "新概念"],
        "priority_boost": 12,
    },
    
    # 融资/并购
    "investment": {
        "name": "融资并购",
        "icon": "💰",
        "keywords": ["融资", "收购", "并购", "投资", "上市", "IPO"],
        "priority_boost": 20,
    },
    
    # 科技赋能
    "technology": {
        "name": "科技赋能",
        "icon": "🔧",
        "keywords": ["数字化", "智能", "AI", "无人", "自助", "系统"],
        "priority_boost": 10,
    },
    
    # 促销活动
    "promotion": {
        "name": "促销活动",
        "icon": "🎁",
        "keywords": ["促销", "优惠", "折扣", "满减", "会员日", "购物节"],
        "priority_boost": 5,
    },
    
    # 供应链
    "supply_chain": {
        "name": "供应链",
        "icon": "📦",
        "keywords": ["供应链", "仓储", "物流", "配送", "采购", "自有品牌"],
        "priority_boost": 8,
    },
    
    # 消费洞察
    "consumer": {
        "name": "消费洞察",
        "icon": "👥",
        "keywords": ["消费者", "消费趋势", "购物习惯", "客流", "复购"],
        "priority_boost": 8,
    },
    
    # 行业报告
    "report": {
        "name": "行业报告",
        "icon": "📊",
        "keywords": ["报告", "数据", "排行", "榜单", "统计", "调研"],
        "priority_boost": 10,
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
