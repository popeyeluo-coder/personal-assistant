# 证券分析数据源

## 国内数据源

### 1. AKShare（推荐）
**优势**：免费、数据全面、更新及时
**使用方式**：
```python
import akshare as ak

# 获取A股历史行情
stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="600519", period="daily", start_date="20200101")

# 获取财务数据
stock_financial_analysis_indicator = ak.stock_financial_analysis_indicator(symbol="600519")

# 获取个股资金流向
stock_individual_fund_flow = ak.stock_individual_fund_flow(stock="600519", market="sh")
```

**文档**：https://akshare.akfamily.xyz/

### 2. Tushare
**优势**：数据质量高、接口稳定
**注意**：需要注册获取token
**使用方式**：
```python
import tushare as ts

ts.set_token('你的token')
pro = ts.pro_api()

# 获取日线行情
df = pro.daily(ts_code='600519.SH', start_date='20200101', end_date='20231231')
```

**文档**：https://tushare.pro/

### 3. 东方财富API
**优势**：数据丰富、覆盖面广
**使用方式**：需分析网页接口

## 国际数据源

### 1. Yahoo Finance
**优势**：免费、覆盖全球市场
**使用方式**：
```python
import yfinance as yf

# 下载股票数据
ticker = yf.Ticker("AAPL")
hist = ticker.history(period="1y")

# 获取财务信息
info = ticker.info
```

**文档**：https://finance.yahoo.com/

### 2. Alpha Vantage
**优势**：免费额度较高
**注意**：需要注册获取API Key
**文档**：https://www.alphavantage.co/

### 3. Financial Modeling Prep (FMP)
**优势**：财务数据详细
**文档**：https://financialmodelingprep.com/

## 数据类型与接口

### 行情数据
- 日线、周线、月线
- 分钟线（1分钟、5分钟、15分钟、30分钟、60分钟）
- 实时tick数据（部分数据源）

### 财务数据
- 资产负债表
- 利润表
- 现金流量表
- 财务指标
- 财务比率

### 行业与宏观数据
- 行业分类
- 行业指数
- 宏观经济指标（GDP、CPI、PPI等）
- 货币政策指标（利率、M2等）

### 资金数据
- 主力资金流向
- 大单交易数据
- 北向资金
- 融资融券数据
- 机构持仓数据

## 数据质量评估标准

### 1. 数据准确性
- 数据来源是否权威
- 是否经过清洗和校验
- 是否有异常值处理

### 2. 数据及时性
- 更新频率
- 延迟时间
- 是否支持实时数据

### 3. 数据完整性
- 数据缺失情况
- 历史数据回溯长度
- 是否有补丁数据

### 4. 数据稳定性
- API稳定性
- 数据源可靠性
- 服务可用性

## 数据存储建议

### 1. 本地存储
```python
# 保存为CSV
df.to_csv('data.csv', index=False)

# 保存为Parquet（推荐，体积小、读取快）
df.to_parquet('data.parquet')

# 保存到数据库
import sqlite3
conn = sqlite3.connect('stock_data.db')
df.to_sql('daily_data', conn, if_exists='append', index=False)
```

### 2. 数据库选择
- **SQLite**：适合小规模数据、本地使用
- **MySQL/PostgreSQL**：适合中等规模数据、多用户
- **MongoDB**：适合非结构化数据
- **ClickHouse**：适合大规模时间序列数据

## 数据获取最佳实践

### 1. 数据更新策略
- 增量更新：只获取最新的数据
- 全量更新：定期全量刷新
- 定时任务：设置自动更新时间点

### 2. 错误处理
```python
import time
from requests.exceptions import RequestException

def fetch_data_with_retry(func, max_retries=3, delay=5):
    """带重试机制的数据获取"""
    for i in range(max_retries):
        try:
            return func()
        except RequestException as e:
            if i < max_retries - 1:
                time.sleep(delay)
            else:
                raise
```

### 3. 数据验证
```python
def validate_data(df, required_columns):
    """验证数据完整性"""
    # 检查必需列
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"缺少必需列: {col}")
    
    # 检查空值
    if df.isnull().all().any():
        raise ValueError("数据全部为空")
    
    # 检查数据类型
    if len(df) == 0:
        raise ValueError("数据为空")
    
    return True
```

## 注意事项

### 1. 法律合规
- 遵守数据使用协议
- 注意数据版权
- 商业使用需获取授权

### 2. 速率限制
- 注意API调用频率限制
- 合理设置请求间隔
- 使用缓存减少重复请求

### 3. 数据安全
- 保护API密钥
- 不要将敏感信息提交到代码仓库
- 加密存储敏感数据

### 4. 成本控制
- 注意免费额度限制
- 监控API使用量
- 选择合适的数据源等级
