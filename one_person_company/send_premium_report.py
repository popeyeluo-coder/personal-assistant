#!/usr/bin/env python3
"""
基于最新搜索结果生成高质量专家日报
直接使用已获取的新闻数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import yaml
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config/api_keys.yaml")

# ============ 今日精选高质量新闻 ============

AI_NEWS = {
    "hardware": {
        "name": "🔧 算力与芯片",
        "icon": "💻",
        "news": [
            {
                "title": "华为MWC 2026首次面向海外展示Atlas 950 SuperPoD智算超节点",
                "description": "华为在MWC 2026上推出算力产品矩阵，包括Atlas 950 SuperPoD智算超节点。单柜64卡为基本单元，最大支持8192张NPU卡高速互联，主要为英伟达主导的高端AI算力市场提供替代方案。",
                "url": "https://k.sina.com.cn/article_5952915705_162d248f906702jzks.html",
                "source": "新浪网",
                "age": "1天前",
                "insight": {
                    "summary": "华为算力出海迈出关键一步，国产AI芯片正式进入国际市场竞争",
                    "implication": "国产算力替代加速，对支付系统的底层算力选型有深远影响。关注华为生态对金融科技基础设施的渗透。",
                    "wechat_pay_action": "评估国产算力对支付系统的适配性，提前布局华为云生态合作，在风控、反欺诈等AI场景试点国产算力"
                }
            },
            {
                "title": "英伟达将在GTC大会发布整合Groq LPU技术的全新推理芯片",
                "description": "英伟达计划在下月GTC开发者大会上发布整合Groq语言处理单元技术的全新推理芯片，黄仁勋称其为'世界从未见过'的全新系统。推理时代正式开启。",
                "url": "https://k.sina.com.cn/article_5953741034_162dee0ea0670390so.html",
                "source": "新浪网",
                "age": "2天前",
                "insight": {
                    "summary": "英伟达加速推理芯片布局，AI从训练向推理迁移的趋势更加明确",
                    "implication": "推理成本将大幅下降，更多AI能力可以实时部署在支付场景。实时风控、智能推荐的计算成本将显著降低。",
                    "wechat_pay_action": "关注推理芯片降本对实时AI应用的影响，加速刷脸支付、智能风控等场景的AI能力升级"
                }
            }
        ]
    },
    "models": {
        "name": "🧠 大模型动态",
        "icon": "🤖",
        "news": [
            {
                "title": "DeepSeek V4即将发布：100万Token上下文窗口+原生多模态能力",
                "description": "DeepSeek将于本周发布V4大模型，拥有100万Token上下文窗口（V3的8倍），原生支持图片、视频与文本生成。内部基准测试显示其编程能力已超越Claude与GPT系列，将深度适配国产算力。",
                "url": "https://www.toutiao.com/article/7612117449982394914/",
                "source": "今日头条",
                "age": "2天前",
                "insight": {
                    "summary": "国产大模型突破性进展，DeepSeek在多模态和长上下文能力上实现弯道超车",
                    "implication": "国产大模型+国产算力的组合正在形成，为国内企业提供了完全自主可控的AI基础设施选择。",
                    "wechat_pay_action": "深入评估DeepSeek在支付场景的应用可能性，特别是智能客服、文档理解、合同分析等场景"
                }
            },
            {
                "title": "阿里云MWC发布百炼专属版：面向金融等高合规行业的Agentic AI平台",
                "description": "阿里云在MWC 2026宣布面向国际市场推出企业级Agentic AI开发平台——百炼专属版，专为金融、医疗、公共服务等高合规行业设计，支持100%物理隔离部署。",
                "url": "https://www.leiphone.com/category/industrynews/hSJAaoRMruFtIEHE.html",
                "source": "雷锋网",
                "age": "1天前",
                "insight": {
                    "summary": "企业级AI平台加速落地，合规性和数据安全成为核心卖点",
                    "implication": "金融行业AI应用进入快车道，合规AI解决方案需求爆发，支付行业也需要匹配的AI能力升级。",
                    "wechat_pay_action": "关注阿里百炼在金融场景的落地案例，评估同类企业级AI平台的合作机会"
                }
            }
        ]
    },
    "applications": {
        "name": "📱 AI应用与Agent",
        "icon": "🚀",
        "news": [
            {
                "title": "乐奇Rokid AI眼镜首发支持Gemini、ChatGPT、DeepSeek四大模型",
                "description": "乐奇Rokid AI眼镜海外版正式接入谷歌Gemini、ChatGPT、DeepSeek及通义千问四大AI大模型，成为行业首款支持Gemini的AI眼镜，可在端云协同架构下实现跨模型自由切换。",
                "url": "https://k.sina.com.cn/article_6192937794_17120bb4202002o5gs.html",
                "source": "新浪网",
                "age": "1天前",
                "insight": {
                    "summary": "AI眼镜成为大模型落地的新载体，多模型接入成标配",
                    "implication": "AI正在从手机、电脑扩展到可穿戴设备，未来支付交互方式可能发生根本性变化。",
                    "wechat_pay_action": "关注AI眼镜等新终端的支付需求，探索AR/VR场景下的支付体验创新"
                }
            },
            {
                "title": "上海人工智能实验室发布MIGM-Shortcut：AI图像生成速度提升4倍",
                "description": "上海人工智能实验室联合多家机构开发MIGM-Shortcut技术，能让图像生成速度提升4倍以上，同时保持图像质量几乎不变，论文已发表。",
                "url": "https://new.qq.com/rain/a/20260302A06AE100",
                "source": "腾讯网",
                "age": "1天前",
                "insight": {
                    "summary": "AIGC底层技术持续突破，生成效率显著提升",
                    "implication": "图像生成能力提升将推动营销物料自动化生成，降低运营成本的同时提升个性化水平。",
                    "wechat_pay_action": "探索AIGC在支付营销场景的应用，如个性化红包封面、动态优惠券等"
                }
            }
        ]
    },
    "industry": {
        "name": "🏢 产业与投资",
        "icon": "💰",
        "news": [
            {
                "title": "OpenAI完成1100亿美元融资，软银英伟达亚马逊领投，估值达7300亿美元",
                "description": "OpenAI正式完成1100亿美元融资，刷新全球私营科技公司单笔融资纪录。软银投资300亿、英伟达投资300亿、亚马逊投资500亿美元，OpenAI跻身全球最具价值私营企业行列。",
                "url": "https://www.sohu.com/a/991631930_121118710",
                "source": "搜狐",
                "age": "2天前",
                "insight": {
                    "summary": "AI领域融资规模创历史新高，头部效应持续加剧",
                    "implication": "巨额资本涌入将加速AI技术迭代和市场洗牌，需要关注产业格局变化对To B生态的影响。",
                    "wechat_pay_action": "关注OpenAI生态的商业化进展，评估其企业服务能力对支付AI解决方案的借鉴意义"
                }
            },
            {
                "title": "马斯克xAI完成200亿美元E轮融资，英伟达思科入局，估值2300亿美元",
                "description": "xAI正式完成E轮融资200亿美元，英伟达、思科等战略投资方入局，将重点投向数据中心规模扩大和Grok模型开发。",
                "url": "https://k.sina.com.cn/article_7857201856_1d45362c001902t62g.html",
                "source": "新浪网",
                "age": "近期",
                "insight": {
                    "summary": "AI领域双雄格局形成，OpenAI与xAI竞争白热化",
                    "implication": "多方巨头竞争有利于技术快速迭代和成本下降，对下游应用是利好。",
                    "wechat_pay_action": "保持对多个AI平台的关注和接入能力，避免单一依赖"
                }
            }
        ]
    }
}

RETAIL_NEWS = {
    "supermarket": {
        "name": "🛒 商超与会员店",
        "icon": "🏪",
        "wechat_pay_angle": "会员体系打通、小程序商城、到家业务支付",
        "news": [
            {
                "title": "山姆年增13家门店、盒马2026年冲刺300店，会员制零售加速扩张",
                "description": "山姆会员店持续快速扩张，盒马则推出超盒算NB新业态进入安徽。上海成为首个同时拥有山姆、奥乐齐、盒马三大零售品牌的城市。",
                "url": "https://caifuhao.eastmoney.com/news/20260303111745231028030",
                "source": "东方财富",
                "age": "1天前",
                "insight": {
                    "summary": "会员制零售持续扩张，差异化竞争格局形成",
                    "implication": "会员经济成为零售竞争焦点，支付+会员的深度融合是差异化的关键机会。",
                    "wechat_pay_action": "推广微信支付会员通解决方案，深化与山姆、盒马的数据打通合作"
                }
            },
            {
                "title": "女性零售高管的2026年：山姆、奥乐齐、盒马三大品牌迎来女性掌舵",
                "description": "2026年山姆、奥乐齐、盒马三家独具特色的零售品牌都将由女性高管带领，直面国内快速迭代的零售市场竞争。",
                "url": "https://www.ebrun.com/20260303/642188.shtml",
                "source": "亿邦动力",
                "age": "1天前",
                "insight": {
                    "summary": "零售行业进入精细化运营阶段，管理层变革或带来策略调整",
                    "implication": "新领导层可能带来新的合作机会，需要关注各品牌战略调整。",
                    "wechat_pay_action": "主动拜访三大品牌新管理层，寻找合作切入点"
                }
            }
        ]
    },
    "discount": {
        "name": "🍬 硬折扣零售",
        "icon": "💸",
        "wechat_pay_angle": "快速收银、无感支付、门店数字化解决方案",
        "news": [
            {
                "title": "奥乐齐2026年Q1中国门店冲刺100家，南京四店齐开深耕长三角",
                "description": "奥乐齐宣布2026年第一季度门店数量将突破100家，南京四店同开进驻建邺、栖霞、江宁、浦口四大核心商圈，90%以上商品为自有品牌。",
                "url": "https://www.toutiao.com/article/7598842519723459114/",
                "source": "今日头条",
                "age": "近期",
                "insight": {
                    "summary": "硬折扣模式获市场认可，奥乐齐加速跑马圈地",
                    "implication": "硬折扣赛道高速增长，新店快速扩张带来大量支付接入需求。",
                    "wechat_pay_action": "针对奥乐齐新店推出标准化快速接入方案，争取成为其首选支付服务商"
                }
            },
            {
                "title": "盒马一天新开17店，奥乐齐再降价30%，硬折扣零售竞争升温",
                "description": "硬折扣商超赛道商战升温：盒马NB升级、奥乐齐再度宣布降价高达30%、美团快乐猴瞄准上海市场。经过两年发展，硬折扣商超成功验证商业可行性。",
                "url": "https://new.qq.com/rain/a/20250906A0228400",
                "source": "腾讯网",
                "age": "近期",
                "insight": {
                    "summary": "硬折扣赛道竞争白热化，价格战持续加剧",
                    "implication": "价格敏感度提升对支付费率也形成压力，需要提供更高性价比的解决方案。",
                    "wechat_pay_action": "针对硬折扣业态推出低费率+增值服务组合方案，用服务差异化替代价格竞争"
                }
            }
        ]
    },
    "dutyfree": {
        "name": "✈️ 免税零售",
        "icon": "🛫",
        "wechat_pay_angle": "境外钱包互通、外卡支付、跨境支付便利化",
        "news": [
            {
                "title": "海南春节离岛免税销售超27亿元，中免cdf三亚单日破2亿",
                "description": "2026年春节假期海南离岛免税销售金额超27亿元同比增长30%以上，购物人数逾32万人次同比增长35%。cdf三亚国际免税城单日销售额突破2亿元。",
                "url": "https://new.qq.com/rain/a/20260226A04SWA00",
                "source": "腾讯网",
                "age": "近期",
                "insight": {
                    "summary": "免税消费强劲复苏，海南自贸港政策红利持续释放",
                    "implication": "入境游恢复和免税政策叠加，跨境支付便利化成为吸引游客的关键。",
                    "wechat_pay_action": "加速外卡支付、境外钱包互通在海南免税场景的落地，提升境外游客支付体验"
                }
            }
        ]
    },
    "convenience": {
        "name": "🏪 便利店",
        "icon": "🌙",
        "wechat_pay_angle": "刷脸支付、小程序点单、会员私域运营",
        "news": [
            {
                "title": "2026年便利店数字化：AI+全场景融合，智能消费更普及",
                "description": "便利店行业数字化转型深入，移动支付、自助结账、智能货架等数字化服务提升顾客购物体验。超六成中型连锁品牌已启动数字化工具升级。",
                "url": "https://www.fanpusoft.com/bld/xz/4879.html",
                "source": "泛普软件",
                "age": "近期",
                "insight": {
                    "summary": "便利店数字化进入精细化阶段，AI能力成新竞争点",
                    "implication": "便利店是高频支付场景，数字化升级带来增值服务和深度合作机会。",
                    "wechat_pay_action": "深化刷脸支付在便利店的部署，推广小程序+企微私域组合方案"
                }
            }
        ]
    },
    "payment": {
        "name": "💳 支付与金融科技",
        "icon": "📲",
        "wechat_pay_angle": "行业趋势洞察、竞品动态、创新机会",
        "news": [
            {
                "title": "数字人民币App新增微信支付钱包快付，支付生态进一步打通",
                "description": "数字人民币(试点版)App已新增微信支付钱包快付，微信App可以使用数字人民币钱包进行支付，支持微信部分小程序等场景。",
                "url": "https://www.163.com/dy/article/HV5DNI75051191D6.html",
                "source": "网易",
                "age": "近期",
                "insight": {
                    "summary": "数字人民币与微信支付生态打通，应用场景加速拓展",
                    "implication": "数字人民币与现有支付生态的融合进入新阶段，需要持续关注政策动向。",
                    "wechat_pay_action": "加速数字人民币在更多场景的接入，特别是政务、交通等重点领域"
                }
            },
            {
                "title": "即时零售行业2026年将破万亿，顺丰同城利润翻倍领跑即配",
                "description": "我国即时零售行业预计2026年将正式突破1万亿元规模，顺丰同城2025年经调整净利同比增长158%以上，连续六个周期盈利。",
                "url": "https://new.qq.com/rain/a/20260303A05VBD00",
                "source": "腾讯网",
                "age": "1天前",
                "insight": {
                    "summary": "即时零售万亿市场形成，履约配送成核心竞争力",
                    "implication": "即时零售的高速增长带来大量线上支付场景，到家业务支付体验是关键。",
                    "wechat_pay_action": "深化与即时零售平台的合作，优化到家业务的支付体验和结算效率"
                }
            }
        ]
    }
}


def generate_ai_report_html():
    """生成AI日报HTML"""
    date = datetime.now().strftime("%Y年%m月%d日")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()]
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 700px; 
            margin: 0 auto; 
            background: #ffffff; 
            border-radius: 16px; 
            overflow: hidden; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{ 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{ 
            font-size: 28px; 
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .header .subtitle {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 12px;
        }}
        .header .date {{ 
            font-size: 15px; 
            opacity: 0.85;
            background: rgba(255,255,255,0.15);
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
        }}
        .top-insight {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            padding: 25px 30px;
            border-left: 4px solid #667eea;
            font-size: 14px;
            line-height: 1.8;
            color: #444;
        }}
        .content {{ padding: 30px; }}
        .dimension {{ 
            margin-bottom: 35px;
            border-bottom: 1px solid #eee;
            padding-bottom: 25px;
        }}
        .dimension:last-child {{ border-bottom: none; }}
        .dimension-header {{ 
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }}
        .dimension-icon {{ font-size: 24px; margin-right: 12px; }}
        .dimension-title {{ font-size: 18px; font-weight: 600; color: #333; }}
        .news-card {{ 
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #eee;
        }}
        .news-title {{ 
            font-size: 15px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
            line-height: 1.5;
        }}
        .news-title a {{ color: #333; text-decoration: none; }}
        .news-title a:hover {{ color: #667eea; }}
        .news-desc {{ 
            font-size: 13px;
            color: #666;
            line-height: 1.7;
            margin-bottom: 15px;
        }}
        .news-meta {{ font-size: 12px; color: #999; margin-bottom: 15px; }}
        .insight-box {{
            background: linear-gradient(135deg, #fff9e6 0%, #fff3cd 100%);
            border-radius: 8px;
            padding: 18px;
            margin-top: 12px;
            border-left: 3px solid #f0ad4e;
        }}
        .insight-title {{ font-size: 13px; font-weight: 600; color: #856404; margin-bottom: 12px; }}
        .insight-item {{ font-size: 13px; color: #856404; line-height: 1.8; margin-bottom: 10px; }}
        .insight-item strong {{ color: #664d03; }}
        .wechat-action {{
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 6px;
            padding: 12px;
            margin-top: 10px;
            font-size: 13px;
            color: #155724;
            line-height: 1.6;
        }}
        .wechat-action strong {{ color: #0d3d19; }}
        .footer {{ 
            background: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            border-top: 1px solid #eee;
        }}
        .footer p {{ color: #666; font-size: 12px; line-height: 1.8; }}
        .footer .brand {{ color: #667eea; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 AI前沿日报</h1>
            <div class="subtitle">每日精选 · 专家解读 · 价值洞察</div>
            <div class="date">{date} {weekday}</div>
        </div>
        
        <div class="top-insight">
            <strong>📊 今日AI领域核心动态</strong><br><br>
            🔧 <strong>算力</strong>：华为MWC首秀Atlas 950 SuperPoD，英伟达GTC将发布革命性推理芯片<br>
            🧠 <strong>大模型</strong>：DeepSeek V4本周发布（100万Token上下文），阿里百炼专属版出海<br>
            🚀 <strong>应用</strong>：AI眼镜接入四大模型，图像生成速度提升4倍<br>
            💰 <strong>投资</strong>：OpenAI 1100亿美元融资创纪录，xAI 200亿美元E轮完成
        </div>
        
        <div class="content">
"""
    
    for dim_key, dim_data in AI_NEWS.items():
        html += f"""
            <div class="dimension">
                <div class="dimension-header">
                    <span class="dimension-icon">{dim_data['icon']}</span>
                    <span class="dimension-title">{dim_data['name']}</span>
                </div>
"""
        for news in dim_data['news']:
            insight = news['insight']
            html += f"""
                <div class="news-card">
                    <div class="news-title"><a href="{news['url']}" target="_blank">{news['title']}</a></div>
                    <div class="news-desc">{news['description']}</div>
                    <div class="news-meta">📎 {news['source']} · {news['age']}</div>
                    
                    <div class="insight-box">
                        <div class="insight-title">💡 专家解读</div>
                        <div class="insight-item"><strong>核心要点：</strong>{insight['summary']}</div>
                        <div class="insight-item"><strong>对你的启示：</strong>{insight['implication']}</div>
                        <div class="wechat-action"><strong>🔗 微信支付机会：</strong>{insight['wechat_pay_action']}</div>
                    </div>
                </div>
"""
        html += "</div>"
    
    html += """
        </div>
        
        <div class="footer">
            <p><span class="brand">🤖 一人公司AI系统</span> · 专家级信息服务</p>
            <p>📰 内容经多轮搜索和AI深度分析，确保专业价值</p>
            <p>💬 如有反馈，回复邮件即可 · 系统持续自我迭代优化</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def generate_retail_report_html():
    """生成零售日报HTML"""
    date = datetime.now().strftime("%Y年%m月%d日")
    weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()]
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif; 
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{ 
            max-width: 700px; 
            margin: 0 auto; 
            background: #ffffff; 
            border-radius: 16px; 
            overflow: hidden; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{ 
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white; 
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 8px; }}
        .header .subtitle {{ font-size: 14px; opacity: 0.9; margin-bottom: 12px; }}
        .header .date {{ 
            font-size: 15px; opacity: 0.85;
            background: rgba(255,255,255,0.15);
            display: inline-block; padding: 6px 16px; border-radius: 20px;
        }}
        .top-insight {{
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            padding: 25px 30px;
            border-left: 4px solid #11998e;
            font-size: 14px;
            line-height: 1.8;
            color: #444;
        }}
        .content {{ padding: 30px; }}
        .dimension {{ 
            margin-bottom: 35px;
            border-bottom: 1px solid #eee;
            padding-bottom: 25px;
        }}
        .dimension:last-child {{ border-bottom: none; }}
        .dimension-header {{ display: flex; align-items: center; margin-bottom: 8px; }}
        .dimension-icon {{ font-size: 24px; margin-right: 12px; }}
        .dimension-title {{ font-size: 18px; font-weight: 600; color: #333; }}
        .dimension-angle {{ 
            font-size: 12px; color: #11998e; 
            margin-bottom: 15px; padding-left: 36px;
        }}
        .news-card {{ 
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #eee;
        }}
        .news-title {{ font-size: 15px; font-weight: 600; color: #333; margin-bottom: 10px; line-height: 1.5; }}
        .news-title a {{ color: #333; text-decoration: none; }}
        .news-title a:hover {{ color: #11998e; }}
        .news-desc {{ font-size: 13px; color: #666; line-height: 1.7; margin-bottom: 15px; }}
        .news-meta {{ font-size: 12px; color: #999; margin-bottom: 15px; }}
        .insight-box {{
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            border-radius: 8px;
            padding: 18px;
            margin-top: 12px;
            border-left: 3px solid #4caf50;
        }}
        .insight-title {{ font-size: 13px; font-weight: 600; color: #2e7d32; margin-bottom: 12px; }}
        .insight-item {{ font-size: 13px; color: #2e7d32; line-height: 1.8; margin-bottom: 10px; }}
        .insight-item strong {{ color: #1b5e20; }}
        .wechat-action {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 6px;
            padding: 12px;
            margin-top: 10px;
            font-size: 13px;
            color: #1565c0;
            line-height: 1.6;
        }}
        .wechat-action strong {{ color: #0d47a1; }}
        .opportunities {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            padding: 25px 30px;
        }}
        .opportunities h3 {{ font-size: 16px; color: #e65100; margin-bottom: 15px; }}
        .opportunity-item {{
            background: white;
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 10px;
            font-size: 13px;
            color: #bf360c;
            border-left: 3px solid #ff9800;
            line-height: 1.6;
        }}
        .opportunity-item strong {{ color: #e65100; }}
        .footer {{ 
            background: #f8f9fa;
            padding: 25px 30px;
            text-align: center;
            border-top: 1px solid #eee;
        }}
        .footer p {{ color: #666; font-size: 12px; line-height: 1.8; }}
        .footer .brand {{ color: #11998e; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛒 零售行业日报</h1>
            <div class="subtitle">深度洞察 · 支付机会 · 行动指南</div>
            <div class="date">{date} {weekday}</div>
        </div>
        
        <div class="top-insight">
            <strong>📊 今日零售行业动态</strong><br><br>
            共筛选 <strong>8</strong> 条高价值信息，覆盖 <strong>5</strong> 个核心赛道<br><br>
            💡 <strong>重点关注</strong>：会员制零售扩张、硬折扣竞争升温、免税消费复苏、即时零售破万亿
        </div>
        
        <div class="content">
"""
    
    for dim_key, dim_data in RETAIL_NEWS.items():
        html += f"""
            <div class="dimension">
                <div class="dimension-header">
                    <span class="dimension-icon">{dim_data['icon']}</span>
                    <span class="dimension-title">{dim_data['name']}</span>
                </div>
                <div class="dimension-angle">💳 支付视角：{dim_data['wechat_pay_angle']}</div>
"""
        for news in dim_data['news']:
            insight = news['insight']
            html += f"""
                <div class="news-card">
                    <div class="news-title"><a href="{news['url']}" target="_blank">{news['title']}</a></div>
                    <div class="news-desc">{news['description']}</div>
                    <div class="news-meta">📎 {news['source']} · {news['age']}</div>
                    
                    <div class="insight-box">
                        <div class="insight-title">💡 专家解读</div>
                        <div class="insight-item"><strong>核心要点：</strong>{insight['summary']}</div>
                        <div class="insight-item"><strong>对你的启示：</strong>{insight['implication']}</div>
                        <div class="wechat-action"><strong>🔗 微信支付行动：</strong>{insight['wechat_pay_action']}</div>
                    </div>
                </div>
"""
        html += "</div>"
    
    html += """
        </div>
        
        <div class="opportunities">
            <h3>💳 微信支付机会汇总</h3>
            <div class="opportunity-item">
                <strong>🛒 商超会员店</strong>：推广微信支付会员通解决方案，深化与山姆、盒马的数据打通合作
            </div>
            <div class="opportunity-item">
                <strong>🍬 硬折扣零售</strong>：针对奥乐齐新店推出标准化快速接入方案，争取成为首选支付服务商
            </div>
            <div class="opportunity-item">
                <strong>✈️ 免税零售</strong>：加速外卡支付、境外钱包互通在海南免税场景的落地
            </div>
            <div class="opportunity-item">
                <strong>🏪 便利店</strong>：深化刷脸支付在便利店的部署，推广小程序+企微私域组合方案
            </div>
            <div class="opportunity-item">
                <strong>📲 即时零售</strong>：深化与即时零售平台的合作，优化到家业务的支付体验和结算效率
            </div>
        </div>
        
        <div class="footer">
            <p><span class="brand">🛒 一人公司AI系统</span> · 零售行业专家服务</p>
            <p>📰 内容经多轮搜索和AI深度分析，聚焦微信支付机会</p>
            <p>💬 如有反馈，回复邮件即可 · 系统持续自我迭代优化</p>
        </div>
    </div>
</body>
</html>
"""
    return html


def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def send_email(to: str, subject: str, html_content: str, config: dict) -> bool:
    """发送HTML邮件"""
    email_config = config.get('notification', {}).get('email', {})
    username = email_config.get('username', '')
    auth_code = email_config.get('auth_code', '')
    
    try:
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        
        with smtplib.SMTP_SSL('smtp.qq.com', 465) as server:
            server.login(username, auth_code)
            server.sendmail(username, [to], msg.as_string())
        
        logger.info(f"✅ 邮件发送成功: {subject}")
        return True
    except Exception as e:
        logger.error(f"❌ 邮件发送失败: {e}")
        return False


def send_wechat(content: str, config: dict) -> bool:
    """发送企微消息"""
    import requests
    
    webhook_url = config.get('notification', {}).get('wechat_bot', {}).get('webhook_url', '')
    if not webhook_url:
        return False
    
    try:
        if len(content) > 4000:
            content = content[:4000] + "\n\n...(更多内容见邮件)"
        
        data = {"msgtype": "markdown", "markdown": {"content": content}}
        response = requests.post(webhook_url, json=data, timeout=10)
        
        if response.status_code == 200 and response.json().get("errcode") == 0:
            logger.info("✅ 企微推送成功")
            return True
        return False
    except Exception as e:
        logger.error(f"❌ 企微推送异常: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("📰 发送高质量专家级日报")
    logger.info("=" * 70)
    
    config = load_config()
    email_username = config.get('notification', {}).get('email', {}).get('username', '')
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 发送AI日报
    logger.info("\n🤖 发送AI前沿日报...")
    ai_html = generate_ai_report_html()
    
    ai_md = f"""# 🤖 AI前沿日报
> {datetime.now().strftime("%Y年%m月%d日")}

## 🔧 算力与芯片
📰 华为MWC首秀Atlas 950 SuperPoD智算超节点
💡 **洞察**: 国产算力出海迈出关键一步

## 🧠 大模型动态
📰 DeepSeek V4本周发布：100万Token上下文
💡 **洞察**: 国产大模型多模态能力弯道超车

## 📱 AI应用与Agent
📰 AI眼镜首发支持四大主流模型
💡 **洞察**: AI正在向可穿戴设备扩展

## 💰 产业与投资
📰 OpenAI 1100亿美元融资创历史纪录
💡 **洞察**: AI领域资本持续涌入

---
*📧 完整版含专家解读已发送至邮箱*"""
    
    send_wechat(ai_md, config)
    send_email(email_username, f"🤖 AI前沿日报（专家版）- {date_str}", ai_html, config)
    
    # 发送零售日报
    logger.info("\n🛒 发送零售行业日报...")
    retail_html = generate_retail_report_html()
    
    retail_md = f"""# 🛒 零售行业日报
> {datetime.now().strftime("%Y年%m月%d日")}

## 🛒 商超与会员店
📰 山姆年增13家、盒马冲刺300店
💡 **洞察**: 会员制零售持续扩张

## 🍬 硬折扣零售
📰 奥乐齐Q1冲刺100家门店
💡 **洞察**: 硬折扣赛道高速增长

## ✈️ 免税零售
📰 海南春节免税销售超27亿元
💡 **洞察**: 免税消费强劲复苏

## 💳 支付与金融科技
📰 数字人民币新增微信支付快付
💡 **洞察**: 支付生态进一步打通

---
*📧 完整版含专家解读和微信支付机会已发送至邮箱*"""
    
    send_wechat(retail_md, config)
    send_email(email_username, f"🛒 零售行业日报（专家版）- {date_str}", retail_html, config)
    
    logger.info("\n" + "=" * 70)
    logger.info("📰 高质量专家级日报发送完成！")
    logger.info("=" * 70)
