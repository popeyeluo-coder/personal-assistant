"""
主入口 - 一人公司AI Agent系统
集成所有服务和Agent的完整运行入口
"""

import os
import sys
import yaml
import json
import logging
from datetime import datetime
from pathlib import Path

# 添加项目路径
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from agents import (
    create_ceo_agent, create_analyst_agent, create_product_agent,
    create_purchase_agent, create_sales_agent, create_finance_agent, create_pm_agent
)
from collaboration.orchestrator import CompanyOrchestrator
from services.api_manager import APIManager, get_api_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / 'logs' / 'company.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class OnePersonCompany:
    """一人公司 - AI Agent驱动的自动化商业系统"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or PROJECT_ROOT / 'config' / 'company_config.yaml'
        self.config = self._load_config()
        
        # 初始化API管理器
        self.api = APIManager()
        
        # 初始化协调器
        self.orchestrator = CompanyOrchestrator()
        self.agents = {}
        
        logger.info("🏢 一人公司初始化中...")
        self._init_agents()
        
    def _load_config(self) -> dict:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"加载配置失败: {e}, 使用默认配置")
            return {}
    
    def _init_agents(self) -> None:
        """初始化所有AI专家"""
        agent_creators = {
            'ceo': create_ceo_agent,
            'analyst': create_analyst_agent,
            'product': create_product_agent,
            'purchase': create_purchase_agent,
            'sales': create_sales_agent,
            'finance': create_finance_agent,
            'pm': create_pm_agent
        }
        
        for agent_type, creator in agent_creators.items():
            agent = creator()
            agent.load_state()
            self.agents[agent_type] = agent
            self.orchestrator.register_agent(agent_type, agent)
            
        logger.info(f"✅ 已初始化 {len(self.agents)} 位AI专家")
    
    def start(self) -> None:
        """启动公司运转"""
        self.orchestrator.start()
        
        # 显示服务状态
        service_status = self.api.get_service_status()
        
        logger.info("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   🏢 一人公司 AI Agent 系统 v1.0                             ║
║                                                              ║
║   ┌─────────────────────────────────────────────────────┐   ║
║   │ 👔 CEO老板      │ 战略决策 │ 任务分配 │ 最终拍板  │   ║
║   │ 📊 商分专家    │ 市场分析 │ 趋势洞察 │ 机会发现  │   ║
║   │ 🔍 选品专家    │ 爆品发现 │ ROI计算  │ 需求验证  │   ║
║   │ 🛒 采购专家    │ 供应商   │ 比价谈判 │ 库存管理  │   ║
║   │ 📢 销售专家    │ 内容创作 │ 流量运营 │ 转化优化  │   ║
║   │ 💰 金融专家    │ 投资分析 │ 交易策略 │ 风险控制  │   ║
║   │ 📋 项目管理    │ 任务跟踪 │ 进度管理 │ 问题解决  │   ║
║   └─────────────────────────────────────────────────────┘   ║
║                                                              ║
║   📡 服务状态:                                               ║
║   • 搜索服务: ✅ Brave Search                                ║
║   • 电商数据: ✅ 抖音/1688/小红书                            ║
║   • 金融数据: ✅ A股/港股/美股                               ║
║   • 通知服务: ✅ QQ邮箱                                      ║
║                                                              ║
║   准备就绪，开始赚钱！💰                                     ║
╚══════════════════════════════════════════════════════════════╝
        """)
    
    def stop(self) -> None:
        """停止公司"""
        self.orchestrator.stop()
        logger.info("🛑 一人公司已停止")
    
    # ==================== 电商业务 ====================
    
    def run_product_discovery(self, category: str = None) -> dict:
        """运行产品发现流程"""
        logger.info(f"🔍 启动产品发现流程 - 品类: {category or '全品类'}")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "stages": {}
        }
        
        # 1. 市场趋势搜索
        logger.info("📊 第1步: 搜索市场趋势...")
        trends = self.api.search.search_trends([
            f"{category} 爆款" if category else "电商爆款",
            f"{category} 热销" if category else "抖音热销",
            "2024 新品趋势"
        ])
        results["stages"]["trends"] = trends
        
        # 2. 商分专家分析
        logger.info("📊 第2步: 商分专家分析...")
        analysis = self.agents['analyst'].process_task({
            'content': {
                'type': 'trend_analysis',
                'domain': category or '电商'
            }
        })
        results["stages"]["market_analysis"] = analysis
        
        # 3. 选品专家评估
        logger.info("🔍 第3步: 选品专家评估...")
        product_eval = self.agents['product'].process_task({
            'content': {
                'type': 'find_product',
                'category': category
            }
        })
        results["stages"]["product_evaluation"] = product_eval
        
        return results
    
    def analyze_product(self, product_name: str) -> dict:
        """分析具体产品"""
        logger.info(f"🔍 分析产品: {product_name}")
        
        results = {
            "product": product_name,
            "timestamp": datetime.now().isoformat(),
            "analysis": {}
        }
        
        # 1. 多平台数据
        logger.info("📊 获取多平台数据...")
        results["analysis"]["platform_data"] = self.api.analyze_product_opportunity(product_name)
        
        # 2. 供应商搜索
        logger.info("🛒 搜索供应商...")
        results["analysis"]["suppliers"] = self.api.ecommerce.search_1688_suppliers(product_name)
        
        # 3. 选品专家评分
        logger.info("⭐ 选品专家评分...")
        results["analysis"]["score"] = self.agents['product'].score_product({
            'name': product_name
        })
        
        # 4. ROI计算
        logger.info("💰 计算ROI...")
        results["analysis"]["roi"] = self.agents['product'].process_task({
            'content': {
                'type': 'calculate_roi',
                'product': {'name': product_name, 'price': 99, 'cost': 30}
            }
        })
        
        return results
    
    # ==================== 金融业务 ====================
    
    def check_watchlist(self) -> dict:
        """检查关注股票"""
        logger.info("📈 检查关注股票...")
        
        # 获取实时数据
        watchlist_data = self.api.get_watchlist()
        
        # 金融专家分析
        analysis = self.agents['finance'].process_task({
            'content': {
                'type': 'portfolio_review'
            }
        })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "watchlist": watchlist_data,
            "analysis": analysis
        }
    
    def analyze_stock(self, stock_code: str, market: str = "A") -> dict:
        """分析单只股票"""
        logger.info(f"📈 分析股票: {stock_code} ({market}股)")
        
        # 获取实时数据
        stock_data = self.api.get_stock_data(stock_code, market)
        
        # 获取相关新闻
        news = self.api.finance.get_stock_news(stock_code)
        
        # 金融专家分析
        analysis = self.agents['finance'].process_task({
            'content': {
                'type': 'stock_analysis',
                'stock': {'code': stock_code, 'market': market}
            }
        })
        
        return {
            "stock_code": stock_code,
            "market": market,
            "timestamp": datetime.now().isoformat(),
            "realtime_data": stock_data,
            "news": news,
            "analysis": analysis
        }
    
    # ==================== 报告和通知 ====================
    
    def generate_daily_report(self) -> str:
        """生成每日报告"""
        logger.info("📝 生成每日报告...")
        
        report = f"""
# 🏢 一人公司每日运营报告

## 📅 报告日期
{datetime.now().strftime('%Y年%m月%d日 %H:%M')}

## 🤖 AI专家团队状态
"""
        for agent_type, agent in self.agents.items():
            status = agent.get_status()
            report += f"\n### {status['name']}\n"
            report += f"- 状态: {'🟢 在线' if status['status'] == 'active' else '🔴 离线'}\n"
            report += f"- 待处理任务: {status['pending_tasks']}\n"
            report += f"- 已完成任务: {status['completed_tasks']}\n"
        
        # 关注股票
        try:
            watchlist = self.api.get_watchlist()
            report += "\n## 📈 关注股票\n"
            report += "| 代码 | 名称 | 现价 | 涨跌幅 |\n"
            report += "|------|------|------|--------|\n"
            for stock in watchlist.get("stocks", []):
                price = stock.get("price", "-")
                change = stock.get("change_pct", 0)
                emoji = "🔴" if change < 0 else "🟢"
                report += f"| {stock.get('code')} | {stock.get('name')} | {price} | {emoji} {change:.2f}% |\n"
        except Exception as e:
            report += f"\n## 📈 关注股票\n获取失败: {e}\n"
        
        report += f"""
## 📊 公司状态
{json.dumps(self.orchestrator.get_company_status(), ensure_ascii=False, indent=2)}

## 📌 下一步行动
1. 继续选品调研
2. 跟进供应商
3. 优化销售策略

---
*由一人公司AI系统自动生成*
"""
        return report
    
    def send_daily_report(self, to: str = None) -> dict:
        """发送每日报告"""
        report = self.generate_daily_report()
        return self.api.send_report(report, to)
    
    # ==================== 自动化运营 ====================
    
    def daily_operation(self) -> dict:
        """每日自动化运营"""
        logger.info("📅 执行每日运营...")
        
        results = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "operations": {}
        }
        
        # 1. CEO站会
        results["operations"]["standup"] = self.agents['ceo'].daily_standup()
        
        # 2. 检查股票
        results["operations"]["watchlist"] = self.check_watchlist()
        
        # 3. 选品巡检
        results["operations"]["product_hunt"] = self.agents['product'].daily_product_hunt()
        
        # 4. 执行待办任务
        for agent_type, agent in self.agents.items():
            results["operations"][f"{agent_type}_tasks"] = agent.execute_pending_tasks()
        
        # 5. PM汇总
        results["operations"]["summary"] = self.agents['pm'].process_task({
            'content': {'type': 'generate_summary', 'period': 'daily'}
        })
        
        return results


def main():
    """主函数 - 交互式运行"""
    company = OnePersonCompany()
    
    try:
        company.start()
        
        while True:
            print("\n" + "=" * 50)
            print("🏢 一人公司控制台")
            print("=" * 50)
            print("1. 🔍 产品发现（选品）")
            print("2. 📊 分析具体产品")
            print("3. 📈 检查股票")
            print("4. 📝 生成日报")
            print("5. 📧 发送日报")
            print("6. ⚙️  服务状态")
            print("7. 🧪 测试服务")
            print("0. 退出")
            print("-" * 50)
            
            choice = input("请选择操作 (0-7): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                category = input("输入品类（回车跳过）: ").strip() or None
                result = company.run_product_discovery(category)
                print(json.dumps(result, ensure_ascii=False, indent=2)[:2000] + "...")
            elif choice == "2":
                product = input("输入产品名称: ").strip()
                if product:
                    result = company.analyze_product(product)
                    print(json.dumps(result, ensure_ascii=False, indent=2)[:2000] + "...")
            elif choice == "3":
                result = company.check_watchlist()
                print(json.dumps(result, ensure_ascii=False, indent=2))
            elif choice == "4":
                report = company.generate_daily_report()
                print(report)
            elif choice == "5":
                result = company.send_daily_report()
                print(f"发送结果: {result}")
            elif choice == "6":
                status = company.api.get_service_status()
                print(json.dumps(status, ensure_ascii=False, indent=2))
            elif choice == "7":
                result = company.api.test_all_services()
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("❌ 无效选择")
                
    except KeyboardInterrupt:
        print("\n收到停止信号...")
    finally:
        company.stop()


if __name__ == '__main__':
    main()
