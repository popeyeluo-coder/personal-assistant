"""
🛒 采购专家 Agent
供应链管理中心 - 全网比货，找到最合适的卖家
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PurchaseAgent(BaseAgent):
    """
    采购专家 - 供应链管理中心
    
    核心能力：
    1. 供应商发现与评估 - 找到优质供应商
    2. 价格谈判策略 - 获取最优价格
    3. 质量把控 - 确保产品质量
    4. 库存管理 - 优化库存周转
    """
    
    def __init__(self, config_path: str = None):
        super().__init__('purchase', config_path)
        
        # 采购专属属性
        self.supplier_database = {}  # 供应商数据库
        self.purchase_orders = []  # 采购订单
        self.price_history = {}  # 价格历史
        self.inventory = {}  # 库存状态
        
        # 采购标准
        self.purchase_criteria = {
            'min_supplier_rating': 4.5,
            'max_delivery_days': 7,
            'min_moq': 10,
            'max_moq': 500,
            'payment_terms': ['款到发货', '月结30天']
        }
        
        # 采购平台
        self.platforms = [
            {'name': '1688', 'priority': 1, 'type': 'B2B'},
            {'name': '拼多多批发', 'priority': 2, 'type': 'B2B'},
            {'name': '义乌购', 'priority': 3, 'type': 'B2B'},
            {'name': '淘工厂', 'priority': 4, 'type': 'OEM'},
            {'name': 'Alibaba', 'priority': 5, 'type': 'Global'}
        ]
        
    def process_task(self, task: Dict) -> Dict:
        """处理采购任务"""
        task_type = task.get('content', {}).get('type', 'find_supplier')
        
        handlers = {
            'find_supplier': self._find_suppliers,
            'compare_prices': self._compare_prices,
            'evaluate_supplier': self._evaluate_supplier,
            'create_order': self._create_order,
            'manage_inventory': self._manage_inventory,
            'negotiate_price': self._negotiate_price
        }
        
        handler = handlers.get(task_type, self._find_suppliers)
        return handler(task)
    
    def _find_suppliers(self, task: Dict) -> Dict:
        """寻找供应商"""
        product = task.get('content', {}).get('product', {})
        product_name = product.get('name', '')
        
        search_result = {
            'timestamp': datetime.now().isoformat(),
            'product': product_name,
            'search_platforms': self.platforms,
            'suppliers_found': [],
            'recommended_suppliers': []
        }
        
        # 模拟搜索各平台
        for platform in self.platforms:
            platform_result = {
                'platform': platform['name'],
                'suppliers': [],
                'price_range': {'min': 0, 'max': 0},
                'avg_rating': 0
            }
            search_result['suppliers_found'].append(platform_result)
        
        return search_result
    
    def _compare_prices(self, task: Dict) -> Dict:
        """比价"""
        product = task.get('content', {}).get('product', {})
        suppliers = task.get('content', {}).get('suppliers', [])
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'product': product.get('name', ''),
            'quantity': product.get('quantity', 100),
            
            'price_comparison': [],
            'best_option': None,
            'recommendation': ''
        }
        
        for supplier in suppliers:
            supplier_price = {
                'supplier_name': supplier.get('name', ''),
                'platform': supplier.get('platform', ''),
                'unit_price': supplier.get('price', 0),
                'moq': supplier.get('moq', 0),
                'shipping_cost': supplier.get('shipping', 0),
                'total_cost': 0,
                'rating': supplier.get('rating', 0),
                'delivery_days': supplier.get('delivery_days', 0)
            }
            
            # 计算总成本
            quantity = product.get('quantity', 100)
            supplier_price['total_cost'] = (
                supplier_price['unit_price'] * quantity + 
                supplier_price['shipping_cost']
            )
            
            comparison['price_comparison'].append(supplier_price)
        
        # 找出最优选项
        if comparison['price_comparison']:
            # 综合考虑价格、评分、配送
            best = min(
                comparison['price_comparison'],
                key=lambda x: x['total_cost'] / (x['rating'] / 5) * (x['delivery_days'] / 7)
            )
            comparison['best_option'] = best
            comparison['recommendation'] = f"推荐选择 {best['supplier_name']}，综合性价比最高"
        
        return comparison
    
    def _evaluate_supplier(self, task: Dict) -> Dict:
        """评估供应商"""
        supplier = task.get('content', {}).get('supplier', {})
        
        evaluation = {
            'timestamp': datetime.now().isoformat(),
            'supplier_name': supplier.get('name', ''),
            'platform': supplier.get('platform', ''),
            
            # 评估维度
            'scores': {
                'price_competitiveness': 0,  # 价格竞争力
                'quality': 0,  # 产品质量
                'reliability': 0,  # 可靠性
                'service': 0,  # 服务水平
                'delivery': 0  # 配送效率
            },
            
            'weights': {
                'price_competitiveness': 0.25,
                'quality': 0.30,
                'reliability': 0.20,
                'service': 0.10,
                'delivery': 0.15
            },
            
            # 详细分析
            'detailed_analysis': {
                'store_age': 0,  # 店铺年限
                'transaction_volume': 0,  # 交易量
                'repeat_customers': 0,  # 回头客比例
                'dispute_rate': 0,  # 纠纷率
                'response_time': 0  # 响应时间
            },
            
            'total_score': 0,
            'grade': '',
            'recommendation': ''
        }
        
        # 计算总分
        total_score = sum(
            evaluation['scores'][k] * evaluation['weights'][k]
            for k in evaluation['scores']
        )
        evaluation['total_score'] = total_score
        
        # 评级
        if total_score >= 90:
            evaluation['grade'] = 'A+'
            evaluation['recommendation'] = '优质供应商，强烈推荐合作'
        elif total_score >= 80:
            evaluation['grade'] = 'A'
            evaluation['recommendation'] = '良好供应商，推荐合作'
        elif total_score >= 70:
            evaluation['grade'] = 'B'
            evaluation['recommendation'] = '合格供应商，可以考虑'
        elif total_score >= 60:
            evaluation['grade'] = 'C'
            evaluation['recommendation'] = '一般供应商，谨慎选择'
        else:
            evaluation['grade'] = 'D'
            evaluation['recommendation'] = '不推荐，建议更换'
        
        # 存入数据库
        self.supplier_database[supplier.get('id', '')] = evaluation
        
        return evaluation
    
    def _create_order(self, task: Dict) -> Dict:
        """创建采购订单"""
        order_details = task.get('content', {}).get('order', {})
        
        order = {
            'order_id': f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'status': 'created',
            
            'supplier': order_details.get('supplier', {}),
            'products': order_details.get('products', []),
            
            'quantities': order_details.get('quantities', {}),
            'unit_prices': order_details.get('prices', {}),
            'total_amount': 0,
            
            'shipping': {
                'method': '',
                'cost': 0,
                'estimated_days': 0
            },
            
            'payment': {
                'method': '',
                'status': 'pending',
                'amount': 0
            },
            
            'notes': ''
        }
        
        # 计算总金额
        total = 0
        for product in order['products']:
            qty = order['quantities'].get(product, 0)
            price = order['unit_prices'].get(product, 0)
            total += qty * price
        
        order['total_amount'] = total + order['shipping']['cost']
        order['payment']['amount'] = order['total_amount']
        
        self.purchase_orders.append(order)
        
        return order
    
    def _manage_inventory(self, task: Dict) -> Dict:
        """管理库存"""
        action = task.get('content', {}).get('action', 'check')
        
        inventory_report = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'inventory_status': {},
            'alerts': [],
            'recommendations': []
        }
        
        if action == 'check':
            # 检查库存状态
            for product_id, stock in self.inventory.items():
                status = {
                    'product_id': product_id,
                    'current_stock': stock.get('quantity', 0),
                    'safety_stock': stock.get('safety_level', 10),
                    'reorder_point': stock.get('reorder_point', 20),
                    'status': 'normal'
                }
                
                if status['current_stock'] <= status['safety_stock']:
                    status['status'] = 'critical'
                    inventory_report['alerts'].append({
                        'product_id': product_id,
                        'message': '库存严重不足，需立即补货',
                        'urgency': 'high'
                    })
                elif status['current_stock'] <= status['reorder_point']:
                    status['status'] = 'low'
                    inventory_report['recommendations'].append({
                        'product_id': product_id,
                        'action': '建议补货',
                        'suggested_quantity': status['reorder_point'] * 2
                    })
                
                inventory_report['inventory_status'][product_id] = status
        
        elif action == 'update':
            # 更新库存
            updates = task.get('content', {}).get('updates', {})
            for product_id, change in updates.items():
                if product_id not in self.inventory:
                    self.inventory[product_id] = {'quantity': 0}
                self.inventory[product_id]['quantity'] += change
        
        return inventory_report
    
    def _negotiate_price(self, task: Dict) -> Dict:
        """议价策略"""
        supplier = task.get('content', {}).get('supplier', {})
        product = task.get('content', {}).get('product', {})
        target_price = task.get('content', {}).get('target_price', 0)
        
        negotiation = {
            'timestamp': datetime.now().isoformat(),
            'supplier': supplier.get('name', ''),
            'product': product.get('name', ''),
            'current_price': product.get('price', 0),
            'target_price': target_price,
            
            'strategies': [
                {
                    'name': '批量折扣',
                    'approach': '承诺更大采购量换取单价优惠',
                    'potential_saving': '5-15%'
                },
                {
                    'name': '长期合作',
                    'approach': '签订长期合作协议获取优惠',
                    'potential_saving': '3-8%'
                },
                {
                    'name': '竞品比价',
                    'approach': '展示竞争对手报价施压',
                    'potential_saving': '5-10%'
                },
                {
                    'name': '付款条件',
                    'approach': '提供更有利的付款条件换取折扣',
                    'potential_saving': '2-5%'
                }
            ],
            
            'talking_points': [],
            'bottom_line': target_price * 1.05,  # 底线留5%空间
            'walk_away_price': target_price * 1.15  # 放弃价格
        }
        
        return negotiation
    
    def calculate_total_cost(self, product: Dict, quantity: int, supplier: Dict) -> Dict:
        """
        计算总采购成本
        
        包含：
        1. 产品成本
        2. 运费
        3. 包装费
        4. 验货费
        5. 其他费用
        """
        unit_price = supplier.get('price', 0)
        shipping_per_unit = supplier.get('shipping_per_unit', 0)
        packaging_fee = supplier.get('packaging_fee', 0)
        
        cost_breakdown = {
            'product_cost': unit_price * quantity,
            'shipping_cost': shipping_per_unit * quantity,
            'packaging_cost': packaging_fee,
            'inspection_cost': 0,
            'other_costs': 0
        }
        
        total_cost = sum(cost_breakdown.values())
        cost_per_unit = total_cost / quantity if quantity > 0 else 0
        
        return {
            'quantity': quantity,
            'breakdown': cost_breakdown,
            'total_cost': total_cost,
            'cost_per_unit': cost_per_unit
        }
    
    def generate_report(self) -> str:
        """生成采购报告"""
        report = f"""
# 🛒 采购管理报告

## 报告概要
- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- 采购专家: {self.name}
- 供应商数量: {len(self.supplier_database)}
- 采购订单数: {len(self.purchase_orders)}

## 采购标准
- 供应商最低评分: {self.purchase_criteria['min_supplier_rating']}
- 最长配送天数: {self.purchase_criteria['max_delivery_days']}天
- MOQ范围: {self.purchase_criteria['min_moq']}-{self.purchase_criteria['max_moq']}

## 采购平台
"""
        for platform in self.platforms:
            report += f"- {platform['name']} (优先级: {platform['priority']})\n"
        
        report += """
## 库存状态
"""
        for product_id, stock in self.inventory.items():
            qty = stock.get('quantity', 0)
            status = '正常' if qty > 20 else ('低库存' if qty > 10 else '⚠️ 紧急')
            report += f"- {product_id}: {qty} 件 [{status}]\n"
        
        report += """
## 近期订单
"""
        for order in self.purchase_orders[-5:]:
            report += f"- {order['order_id']}: ¥{order['total_amount']:.2f} [{order['status']}]\n"
        
        report += """
## 下一步行动
1. 跟进待发货订单
2. 补充低库存产品
3. 评估新供应商

---
*由采购专家 Agent 自动生成*
"""
        return report


# 便捷创建函数
def create_purchase_agent(config_path: str = None) -> PurchaseAgent:
    """创建采购专家 Agent实例"""
    return PurchaseAgent(config_path)
