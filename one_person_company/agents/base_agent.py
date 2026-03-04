"""
AI专家Agent基类
所有专家Agent都继承自此基类
"""

import os
import yaml
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """AI专家Agent基类"""
    
    def __init__(self, agent_type: str, config_path: str = None):
        """
        初始化Agent
        
        Args:
            agent_type: Agent类型 (ceo/analyst/product/purchase/sales/finance/pm)
            config_path: 配置文件路径
        """
        self.agent_type = agent_type
        self.config = self._load_config(config_path)
        self.agent_config = self.config.get(agent_type, {})
        self.name = self.agent_config.get('name', agent_type)
        self.role = self.agent_config.get('role', '')
        self.model = self.agent_config.get('model', 'claude-sonnet-4-20250514')
        self.temperature = self.agent_config.get('temperature', 0.7)
        self.system_prompt = self.agent_config.get('prompts', {}).get('system', '')
        
        # 知识库 - 用于自我学习
        self.knowledge_base = {}
        self.learning_history = []
        
        # 任务队列
        self.task_queue = []
        self.completed_tasks = []
        
        logger.info(f"🤖 {self.name} 已上线，职责：{self.role}")
    
    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置文件"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config' / 'agents_config.yaml'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return {}
    
    @abstractmethod
    def process_task(self, task: Dict) -> Dict:
        """
        处理任务 - 子类必须实现
        
        Args:
            task: 任务详情
            
        Returns:
            处理结果
        """
        pass
    
    @abstractmethod
    def generate_report(self) -> str:
        """生成工作报告 - 子类必须实现"""
        pass
    
    def receive_message(self, message: Dict) -> Dict:
        """
        接收来自其他Agent的消息
        
        Args:
            message: 消息内容
                - from: 发送者
                - type: 消息类型 (task/info/query/feedback)
                - content: 消息内容
                - priority: 优先级 (1-5, 1最高)
        
        Returns:
            响应消息
        """
        logger.info(f"📨 {self.name} 收到来自 {message.get('from')} 的消息")
        
        msg_type = message.get('type', 'info')
        
        if msg_type == 'task':
            return self._handle_task_message(message)
        elif msg_type == 'query':
            return self._handle_query_message(message)
        elif msg_type == 'feedback':
            return self._handle_feedback_message(message)
        else:
            return self._handle_info_message(message)
    
    def _handle_task_message(self, message: Dict) -> Dict:
        """处理任务消息"""
        task = {
            'id': f"task_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'from': message.get('from'),
            'content': message.get('content'),
            'priority': message.get('priority', 3),
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        self.task_queue.append(task)
        self.task_queue.sort(key=lambda x: x['priority'])
        
        return {
            'status': 'accepted',
            'task_id': task['id'],
            'message': f"{self.name} 已接收任务，当前队列: {len(self.task_queue)} 个任务"
        }
    
    def _handle_query_message(self, message: Dict) -> Dict:
        """处理查询消息"""
        # 子类可以重写此方法提供更具体的查询处理
        return {
            'status': 'success',
            'from': self.agent_type,
            'response': f"{self.name} 收到查询，正在处理..."
        }
    
    def _handle_feedback_message(self, message: Dict) -> Dict:
        """处理反馈消息 - 用于自我学习"""
        feedback = message.get('content', {})
        self.learning_history.append({
            'timestamp': datetime.now().isoformat(),
            'feedback': feedback,
            'from': message.get('from')
        })
        return {
            'status': 'learned',
            'message': f"{self.name} 已记录反馈，将用于优化"
        }
    
    def _handle_info_message(self, message: Dict) -> Dict:
        """处理信息消息"""
        return {
            'status': 'received',
            'message': f"{self.name} 已收到信息"
        }
    
    def send_message(self, to_agent: str, message_type: str, content: Any, priority: int = 3) -> Dict:
        """
        向其他Agent发送消息
        
        Args:
            to_agent: 目标Agent
            message_type: 消息类型
            content: 消息内容
            priority: 优先级
            
        Returns:
            消息对象
        """
        message = {
            'from': self.agent_type,
            'to': to_agent,
            'type': message_type,
            'content': content,
            'priority': priority,
            'timestamp': datetime.now().isoformat()
        }
        logger.info(f"📤 {self.name} 向 {to_agent} 发送 {message_type} 消息")
        return message
    
    def learn(self, experience: Dict) -> None:
        """
        自我学习 - 从经验中学习
        
        Args:
            experience: 经验数据
                - type: 经验类型 (success/failure/insight)
                - context: 上下文
                - outcome: 结果
                - lesson: 教训/心得
        """
        learning_record = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.agent_type,
            'experience': experience
        }
        self.learning_history.append(learning_record)
        
        # 更新知识库
        exp_type = experience.get('type', 'insight')
        if exp_type not in self.knowledge_base:
            self.knowledge_base[exp_type] = []
        self.knowledge_base[exp_type].append(experience)
        
        logger.info(f"📚 {self.name} 学习了新经验: {experience.get('lesson', '')[:50]}...")
    
    def iterate(self) -> Dict:
        """
        自我迭代 - 基于学习历史优化自己
        
        Returns:
            迭代报告
        """
        if not self.learning_history:
            return {'status': 'no_data', 'message': '暂无学习记录'}
        
        # 分析成功和失败案例
        successes = [l for l in self.learning_history 
                    if l.get('experience', {}).get('type') == 'success']
        failures = [l for l in self.learning_history 
                   if l.get('experience', {}).get('type') == 'failure']
        
        iteration_report = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.agent_type,
            'total_experiences': len(self.learning_history),
            'success_count': len(successes),
            'failure_count': len(failures),
            'success_rate': len(successes) / len(self.learning_history) if self.learning_history else 0,
            'insights': self._extract_insights(),
            'improvements': self._suggest_improvements()
        }
        
        logger.info(f"🔄 {self.name} 完成自我迭代，成功率: {iteration_report['success_rate']:.2%}")
        return iteration_report
    
    def _extract_insights(self) -> List[str]:
        """从学习历史中提取洞察"""
        insights = []
        for record in self.learning_history[-10:]:  # 最近10条
            exp = record.get('experience', {})
            if 'lesson' in exp:
                insights.append(exp['lesson'])
        return insights
    
    def _suggest_improvements(self) -> List[str]:
        """基于失败案例建议改进"""
        improvements = []
        failures = [l for l in self.learning_history 
                   if l.get('experience', {}).get('type') == 'failure']
        
        for failure in failures[-5:]:  # 最近5个失败案例
            context = failure.get('experience', {}).get('context', '')
            improvements.append(f"避免: {context[:100]}")
        
        return improvements
    
    def get_status(self) -> Dict:
        """获取Agent状态"""
        return {
            'name': self.name,
            'role': self.role,
            'status': 'active',
            'pending_tasks': len(self.task_queue),
            'completed_tasks': len(self.completed_tasks),
            'knowledge_items': sum(len(v) for v in self.knowledge_base.values()),
            'learning_records': len(self.learning_history)
        }
    
    def execute_pending_tasks(self) -> List[Dict]:
        """执行所有待处理任务"""
        results = []
        while self.task_queue:
            task = self.task_queue.pop(0)
            task['status'] = 'processing'
            
            try:
                result = self.process_task(task)
                task['status'] = 'completed'
                task['result'] = result
                self.completed_tasks.append(task)
                
                # 学习成功经验
                self.learn({
                    'type': 'success',
                    'context': task['content'],
                    'outcome': result,
                    'lesson': f"成功完成任务: {task['id']}"
                })
                
            except Exception as e:
                task['status'] = 'failed'
                task['error'] = str(e)
                
                # 学习失败经验
                self.learn({
                    'type': 'failure',
                    'context': task['content'],
                    'outcome': str(e),
                    'lesson': f"任务失败: {str(e)}"
                })
            
            results.append(task)
        
        return results
    
    def save_state(self, path: str = None) -> None:
        """保存Agent状态"""
        if path is None:
            path = Path(__file__).parent.parent / 'data' / f'{self.agent_type}_state.json'
        
        state = {
            'agent_type': self.agent_type,
            'timestamp': datetime.now().isoformat(),
            'knowledge_base': self.knowledge_base,
            'learning_history': self.learning_history[-100:],  # 保留最近100条
            'completed_tasks': self.completed_tasks[-50:]  # 保留最近50个
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 {self.name} 状态已保存")
    
    def load_state(self, path: str = None) -> bool:
        """加载Agent状态"""
        if path is None:
            path = Path(__file__).parent.parent / 'data' / f'{self.agent_type}_state.json'
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.knowledge_base = state.get('knowledge_base', {})
            self.learning_history = state.get('learning_history', [])
            self.completed_tasks = state.get('completed_tasks', [])
            
            logger.info(f"📂 {self.name} 状态已恢复")
            return True
        except FileNotFoundError:
            logger.info(f"📂 {self.name} 无历史状态，从零开始")
            return False
        except Exception as e:
            logger.error(f"加载状态失败: {e}")
            return False
    
    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} - {self.role}>"
