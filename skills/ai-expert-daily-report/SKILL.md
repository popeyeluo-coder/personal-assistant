---
name: ai-expert-daily-report
description: This skill should be used when generating expert-level AI industry daily reports, analyzing AI technology trends, breakthroughs, industry dynamics, and providing actionable insights. It integrates global AI model knowledge and expert content to deliver comprehensive, professional, and forward-thinking AI daily reports with self-iteration capabilities based on user feedback.
---

# AI Expert Daily Report Skill

## Purpose

Generate expert-level daily reports for the AI industry by integrating global AI model knowledge, expert insights, and multi-source intelligence. This skill provides comprehensive analysis of AI technology trends, breakthroughs, industry dynamics, market movements, and strategic insights with continuous self-iteration capabilities.

## When to Use

Use this skill when:
- Generating daily AI industry reports
- Analyzing AI technology trends and breakthroughs
- Tracking major AI companies and research institutions
- Providing strategic insights and actionable recommendations
- Creating AI market analysis and investment insights
- Analyzing AI applications across different industries
- Responding to user feedback to improve report quality

## Skill Usage Workflow

### 1. Data Collection and Integration

Leverage the `collectors/data_collector.py` module to gather comprehensive AI intelligence:

```python
from collectors.data_collector import collect_ai_news

# Collect comprehensive AI news with expert filtering
ai_data = collect_ai_news()
```

The collector automatically:
- Searches core AI topics (GPT-5, Claude, LLaMA, etc.)
- Monitors major AI companies (OpenAI, Anthropic, Google, Meta, etc.)
- Tracks AI research breakthroughs from arXiv and top conferences
- Captures AI application scenarios across industries
- Filters high-value content using relevance scoring

### 2. Expert-Level Analysis

Apply the `analyzers/data_analyzer.py` module for deep analysis:

```python
from analyzers.data_analyzer import analyze_ai_news

# Analyze collected news with expert perspective
analysis_results = analyze_ai_news(ai_data)
```

The analyzer provides:
- **Technology Trend Analysis**: Emerging technologies, breakthrough trajectories, technical challenges
- **Market Dynamics**: Industry developments, competitive landscape, investment trends
- **Company Strategy**: Major players' moves, strategic initiatives, product launches
- **Application Scenarios**: Industry adoption, use case evolution, deployment patterns
- **Risk Assessment**: Technical risks, ethical considerations, regulatory impacts

### 3. Expert Insight Generation

Use expert knowledge from `references/` to enhance analysis:

- `references/ai_technologies.md`: Core AI technologies and their evolution paths
- `references/ai_companies.md`: In-depth profiles of major AI companies and their strategies
- `references/ai_applications.md`: AI application scenarios across different industries
- `references/ai_trends.md`: Emerging trends and future predictions

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

### 4. Global Model Integration

Integrate insights from leading AI models and research:

- **GPT Series**: Understanding the latest capabilities and limitations
- **Claude Family**: Analyzing Anthropic's safety and alignment approach
- **LLaMA/Open Models**: Tracking open-source ecosystem developments
- **Chinese AI Models**: Monitoring progress from Baidu, Alibaba, Tencent, etc.

### 5. Report Generation

Generate comprehensive daily reports using `reports/report_generator.py`:

```python
from reports.report_generator import generate_ai_report

# Generate expert-level daily report
html_report = generate_ai_report(analysis_results)
```

Report structure:
- **Executive Summary**: Key highlights and strategic insights
- **Technology Breakthroughs**: Latest technical advancements
- **Industry Dynamics**: Market movements and company news
- **Application Highlights**: Notable AI deployments
- **Expert Insights**: Forward-looking analysis and recommendations
- **Risk Alerts**: Potential risks and mitigation strategies

### 6. Self-Iteration and Evolution

Implement continuous improvement based on user feedback:

#### Feedback Collection

After sending reports, collect user feedback:
- Email replies and comments
- WeChat work group discussions
- Direct feedback channels

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
        "specific_topics": []
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
      "LLM breakthroughs",
      "AI safety research",
      "Enterprise AI adoption"
    ],
    "report_length": "comprehensive",
    "insight_depth": "expert",
    "risk_tolerance": "balanced"
  },
  "performance_metrics": {
    "user_satisfaction_score": 4.5,
    "feedback_response_rate": 0.8,
    "report_open_rate": 0.9
  },
  "iteration_history": [
    {
      "date": "2026-03-05",
      "changes": [
        "Enhanced safety research coverage",
        "Added enterprise AI metrics",
        "Improved trend prediction accuracy"
      ],
      "feedback_summary": "Users requested more enterprise-focused content"
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

### AI Technology Taxonomy

Leverage comprehensive AI technology understanding:

- **Foundation Models**: LLMs, multimodal models, diffusion models
- **AI Infrastructure**: Training infrastructure, deployment platforms, chip technologies
- **AI Safety and Alignment**: Safety research, alignment techniques, ethical considerations
- **AI Applications**: Enterprise AI, consumer AI, scientific AI, creative AI
- **AI Research**: Top conferences (NeurIPS, ICML, ICLR), key papers, research trends

### Industry Ecosystem

Maintain up-to-date knowledge of:

- **Major AI Companies**: OpenAI, Anthropic, Google DeepMind, Meta AI, Microsoft, Amazon, Baidu, Alibaba, Tencent, ByteDance
- **Research Institutions**: OpenAI, DeepMind, FAIR, Google Brain, Microsoft Research, leading universities
- **Open Source Community**: Hugging Face, EleutherAI, Stability AI, model zoos
- **Startup Landscape**: Emerging companies, funding trends, acquisition patterns

### Market Intelligence

Track:
- **Investment Trends**: VC funding, M&A activity, IPOs
- **Market Sizing**: AI market growth projections, segment analysis
- **Adoption Metrics**: Enterprise adoption rates, developer ecosystem growth
- **Regulatory Landscape**: AI regulations, policy developments, international standards

## Best Practices

1. **Balance Depth and Breadth**: Provide comprehensive coverage while highlighting key insights
2. **Maintain Objectivity**: Present facts and balanced analysis without bias
3. **Forward-Looking**: Include strategic insights and future predictions
4. **Actionable Recommendations**: Provide concrete, actionable advice
5. **Continuous Learning**: Regularly update knowledge base and adapt to new developments
6. **User-Centric**: Tailor content based on user feedback and preferences
7. **Quality Over Quantity**: Focus on high-value, impactful information

## Performance Monitoring

Track key metrics:

- **User Engagement**: Report open rates, read time, feedback frequency
- **Content Quality**: User satisfaction scores, perceived relevance
- **Timeliness**: Report delivery time vs. planned time
- **Accuracy**: Fact-checking results, prediction accuracy
- **Improvement Rate**: Skill iteration effectiveness over time

## Emergency Protocols

Handle special situations:

- **Major Breaking News**: Issue immediate alerts if significant AI news breaks
- **Critical Security Issues**: Prioritize AI safety and security incidents
- **Market Disruptions**: Alert on major market shifts or company crises
- **Technical Failures**: Implement fallback mechanisms if data collection fails

## Contact and Support

For skill-related issues or feedback:
- Email: 709703094@qq.com
- GitHub: https://github.com/popeyeluo-coder/personal-assistant
- Skill Version: 1.0.0
- Last Updated: 2026-03-05
