---
name: mobile-payment-expert
description: This skill should be used when generating expert-level mobile payment industry reports, analyzing WeChat Pay, Alipay (including Alipay touch payment), Douyin Payment, and retail payment dynamics. It integrates global payment model knowledge, expert insights, and market intelligence to deliver comprehensive payment industry analysis with self-iteration capabilities based on user feedback.
---

# Mobile Payment Expert Skill

## Purpose

Generate expert-level reports and analysis for the mobile payment industry by integrating global payment system knowledge, expert insights, and multi-source intelligence. This skill provides comprehensive analysis of WeChat Pay, Alipay, Douyin Payment, retail payment dynamics, market trends, and strategic insights with continuous self-iteration capabilities.

## When to Use

Use this skill when:
- Generating daily/weekly mobile payment industry reports
- Analyzing payment technology trends and innovations
- Tracking major payment platforms and their strategies
- Monitoring retail payment dynamics and merchant adoption
- Analyzing payment ecosystem evolution and competition
- Providing strategic insights for payment businesses
- Responding to user feedback to improve report quality

## Skill Usage Workflow

### 1. Data Collection and Integration

Leverage the `collectors/data_collector.py` module to gather comprehensive payment intelligence:

```python
from collectors.data_collector import collect_payment_news

# Collect comprehensive payment news with expert filtering
payment_data = collect_payment_news()
```

The collector automatically:
- Searches WeChat Pay updates, features, and merchant programs
- Monitors Alipay innovations including "touch payment" (碰一下)
- Tracks Douyin Payment developments and social commerce integration
- Captures retail payment dynamics and merchant adoption trends
- Filters high-value content using relevance scoring

### 2. Expert-Level Analysis

Apply the `analyzers/data_analyzer.py` module for deep analysis:

```python
from analyzers.data_analyzer import analyze_payment_news

# Analyze collected news with expert perspective
analysis_results = analyze_payment_news(payment_data)
```

The analyzer provides:
- **Technology Innovation Analysis**: NFC, QR code, biometric payment trends
- **Market Dynamics**: Payment platform competition, market share shifts
- **Merchant Ecosystem**: Adoption rates, integration challenges, success stories
- **Consumer Behavior**: Payment preferences, adoption barriers, satisfaction
- **Regulatory Landscape**: Payment regulations, policy changes, compliance

### 3. Expert Insight Generation

Use expert knowledge from `references/` to enhance analysis:

- `references/wechat_pay.md`: WeChat Pay features, ecosystem, merchant solutions
- `references/alipay.md`: Alipay platform, touch payment technology, innovations
- `references/douyin_payment.md`: Douyin Payment, social commerce integration
- `references/retail_payment.md`: Retail payment dynamics, merchant adoption, POS systems
- `references/payment_trends.md`: Emerging trends, future predictions, global comparison

Load reference materials dynamically when analyzing specific topics:
```python
import os
from pathlib import Path

def load_reference(topic):
    ref_path = Path(__file__).parent / "references" / f"{topic}.md"
    if ref_path.exists():
        with open(ref_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""
```

### 4. Global Payment System Integration

Integrate insights from global payment systems and best practices:

- **China**: WeChat Pay, Alipay, Douyin Payment, UnionPay
- **Global**: Apple Pay, Google Pay, Samsung Pay, PayPal
- **Southeast Asia**: GrabPay, GoPay, Dana, MoMo
- **Europe**: Swish, Blik, iDEAL, Revolut
- **Emerging Markets**: Mobile money, QR payment adoption

### 5. Report Generation

Generate comprehensive reports using `reports/report_generator.py`:

```python
from reports.report_generator import generate_payment_report

# Generate expert-level payment report
html_report = generate_payment_report(analysis_results)
```

Report structure:
- **Executive Summary**: Key highlights and strategic insights
- **Platform Updates**: New features, product launches, strategic initiatives
- **Technology Innovations**: New payment technologies, UX improvements
- **Market Dynamics**: Competition, partnerships, market share changes
- **Retail Insights**: Merchant adoption, success stories, challenges
- **Regulatory Updates**: Policy changes, compliance requirements
- **Expert Insights**: Forward-looking analysis and recommendations

### 6. Self-Iteration and Evolution

Implement continuous improvement based on user feedback:

#### Feedback Collection

After sending reports, collect user feedback:
- Email replies and comments
- WeChat work group discussions
- Direct feedback channels
- Payment industry professional networks

#### Feedback Analysis

Analyze feedback to identify improvement areas:

```python
def analyze_feedback(feedback_data):
    """Analyze user feedback to improve report quality"""
    
    # Categorize feedback types
    feedback_categories = {
        "content_relevance": [],
        "insight_quality": [],
        "report_format": [],
        "timeliness": [],
        "specific_platforms": []
    }
    
    # Extract actionable insights
    improvements = []
    
    # Update skill configuration
    update_skill_config(improvements)
    
    return improvements
```

#### Skill Configuration Updates

Maintain `config/skill_config.json` to track skill evolution:

```json
{
  "version": "1.0.0",
  "last_updated": "2026-03-05",
  "user_preferences": {
    "focus_areas": [
      "WeChat Pay merchant solutions",
      "Alipay touch payment adoption",
      "Retail payment innovation",
      "Social commerce payment"
    ],
    "report_length": "comprehensive",
    "insight_depth": "expert",
    "platform_coverage": ["wechat", "alipay", "douyin", "retail"]
  },
  "performance_metrics": {
    "user_satisfaction_score": 4.6,
    "feedback_response_rate": 0.85,
    "report_open_rate": 0.92
  },
  "iteration_history": [
    {
      "date": "2026-03-05",
      "changes": [
        "Enhanced Alipay touch payment coverage",
        "Added retail merchant case studies",
        "Improved social commerce payment analysis"
      ],
      "feedback_summary": "Users requested more merchant adoption details"
    }
  ]
}

#### Automatic Keyword Optimization

Implement monthly keyword optimization (1st and 15th of each month):

```python
def optimize_keywords():
    """Automatically optimize search keywords based on report performance"""
    
    # Analyze which topics generate most engagement
    high_engagement_topics = analyze_report_engagement()
    
    # Update search keywords in collectors/data_collector.py
    update_search_keywords(high_engagement_topics)
    
    # Adjust relevance scoring weights
    adjust_scoring_weights()
    
    # Log optimization results
    log_optimization_changes()
```

### 7. Multi-Channel Distribution

Distribute reports through multiple channels:

```python
from utils.email_sender import send_report
from utils.wecom_sender import send_wecom_report

# Email distribution
send_report(html_report, today_str)

# WeChat Work distribution
send_wecom_report(analysis_results, today_str)
```

## Expert Knowledge Integration

### Payment Platform Ecosystem

#### WeChat Pay (微信支付)
- **Core Features**: QR code payments, Mini Program payments, in-app payments
- **Merchant Solutions**: Smart POS, merchant management, marketing tools
- **Ecosystem**: Mini Programs, WeChat Pay Score (微信支付分), WeChat Pay Plus
- **Recent Updates**: New merchant incentives, improved UX, enhanced security

#### Alipay (支付宝)
- **Core Features**: QR payments, Alipay+, merchant services
- **Touch Payment (碰一下)**: NFC-based contactless payment
- **Ecosystem**: Alipay Mini Programs, Ant Forest, Yu'e Bao
- **Recent Updates**: Touch payment expansion, merchant subsidies, new use cases

#### Douyin Payment (抖音支付)
- **Core Features**: In-app payments, social commerce integration
- **Ecosystem**: Livestream shopping, short-video commerce
- **Recent Updates**: Enhanced merchant tools, improved UX, new payment features

### Retail Payment Dynamics

#### Merchant Adoption Patterns
- **QR Code Payments**: Universal adoption across retail
- **NFC Payments**: Growing adoption, especially in urban areas
- **Touch Payment**: Emerging technology, early adoption phase
- **Social Commerce**: Rapid growth, especially in younger demographics

#### Integration Challenges
- **POS Integration**: Legacy systems vs. modern solutions
- **Cost Structure**: Transaction fees, merchant fees
- **User Education**: Teaching new payment methods
- **Competition**: Multiple payment options, user fragmentation

### Technology Landscape

#### Payment Technologies
- **QR Code**: Universal, low-cost, widely adopted
- **NFC**: Contactless, faster, requires hardware upgrades
- **Biometric**: Fingerprint, face recognition, voice payments
- **Touch Payment (碰一下)**: NFC-based, tap-to-pay experience

#### Innovation Trends
1. **Seamless Payments**: Reduced friction, one-tap payments
2. **Multi-Modal**: Combining QR, NFC, biometric for flexibility
3. **AI-Powered**: Personalized offers, fraud detection, analytics
4. **Omnichannel**: Consistent experience across online and offline

### Competitive Dynamics

#### Platform Competition
- **WeChat Pay vs. Alipay**: Dominant duopoly, constant innovation
- **Douyin Payment**: Growing social commerce presence
- **Traditional Banks**: Digital transformation, new payment solutions
- **International Players**: Apple Pay, Google Pay in China

#### Market Share Dynamics
- **WeChat Pay**: ~40-45% market share
- **Alipay**: ~45-50% market share
- **Others**: ~5-10% (Douyin, UnionPay, etc.)

## Best Practices

1. **Balance Breadth and Depth**: Cover all platforms while diving deep into key topics
2. **Merchant-Centric**: Focus on merchant adoption, challenges, and success stories
3. **Technology Focus**: Explain technical innovations in accessible terms
4. **Market Intelligence**: Provide actionable insights for business decisions
5. **Data-Driven**: Use metrics and data to support analysis
6. **User Feedback**: Continuously improve based on reader feedback
7. **Timeliness**: Highlight breaking news and rapid developments

## Performance Monitoring

Track key metrics:
- **User Engagement**: Report open rates, read time, feedback frequency
- **Content Quality**: User satisfaction scores, perceived relevance
- **Timeliness**: Report delivery time vs. planned time
- **Accuracy**: Fact-checking results, prediction accuracy
- **Improvement Rate**: Skill iteration effectiveness over time

## Emergency Protocols

Handle special situations:
- **Major Platform Updates**: Issue immediate alerts on significant feature launches
- **Regulatory Changes**: Alert on important policy or regulation changes
- **Security Incidents**: Prioritize security vulnerabilities or breaches
- **Market Disruptions**: Alert on major market shifts or platform crises

## Contact and Support

For skill-related issues or feedback:
- Email: 709703094@qq.com
- GitHub: https://github.com/popeyeluo-coder/personal-assistant
- Skill Version: 1.0.0
- Last Updated: 2026-03-05
