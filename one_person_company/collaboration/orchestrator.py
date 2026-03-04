"""
协作系统 - Agent之间的消息总线和任务协调
"""

from typing import Dict, List, Any, Callable
from datetime import datetime
from collections import defaultdict
import logging
import json
import threading
from queue import Queue, Empty

logger = logging.getLogger(__name__)


class MessageBus:
    """消息总线 - Agent间通信中枢"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_queue = Queue()
        self.message_history = []
        self.running = False
        
    def subscribe(self, topic: str, handler: Callable) -> None:
        """订阅主题"""
        self.subscribers[topic].append(handler)
        logger.info(f"📌 新订阅: {topic}")
        
    def unsubscribe(self, topic: str, handler: Callable) -> None:
        """取消订阅"""
        if handler in self.subscribers[topic]:
            self.subscribers[topic].remove(handler)
            
    def publish(self, topic: str, message: Dict) -> None:
        """发布消息"""
        msg = {
            'id': f"msg_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            'topic': topic,
            'payload': message,
            'timestamp': datetime.now().isoformat()
        }
        self.message_queue.put(msg)
        self.message_history.append(msg)
        logger.info(f"📤 发布消息到 {topic}")
        
    def process_messages(self) -> None:
        """处理消息队列"""
        while self.running:
            try:
                msg = self.message_queue.get(timeout=1)
                topic = msg['topic']
                for handler in self.subscribers.get(topic, []):
                    try:
                        handler(msg['payload'])
                    except Exception as e:
                        logger.error(f"消息处理失败: {e}")
            except Empty:
                continue
                
    def start(self) -> None:
        """启动消息总线"""
        self.running = True
        self.processor_thread = threading.Thread(target=self.process_messages)
        self.processor_thread.start()
        logger.info("🚀 消息总线已启动")
        
    def stop(self) -> None:
        """停止消息总线"""
        self.running = False
        if hasattr(self, 'processor_thread'):
            self.processor_thread.join()
        logger.info("🛑 消息总线已停止")


class TaskQueue:
    """任务队列 - 管理跨Agent任务"""
    
    def __init__(self):
        self.tasks = []
        self.completed = []
        self.failed = []
        
    def add_task(self, task: Dict) -> str:
        """添加任务"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        task_record = {
            'id': task_id,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            **task
        }
        self.tasks.append(task_record)
        return task_id
        
    def get_next_task(self, agent_type: str = None) -> Dict:
        """获取下一个任务"""
        for task in self.tasks:
            if task['status'] == 'pending':
                if agent_type is None or task.get('assigned_to') == agent_type:
                    task['status'] = 'in_progress'
                    return task
        return None
        
    def complete_task(self, task_id: str, result: Dict) -> None:
        """完成任务"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = 'completed'
                task['result'] = result
                task['completed_at'] = datetime.now().isoformat()
                self.completed.append(task)
                self.tasks.remove(task)
                break
                
    def fail_task(self, task_id: str, error: str) -> None:
        """标记任务失败"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['status'] = 'failed'
                task['error'] = error
                self.failed.append(task)
                self.tasks.remove(task)
                break


class CompanyOrchestrator:
    """公司协调器 - 管理所有Agent的协作"""
    
    def __init__(self):
        self.agents = {}
        self.message_bus = MessageBus()
        self.task_queue = TaskQueue()
        
    def register_agent(self, agent_type: str, agent) -> None:
        """注册Agent"""
        self.agents[agent_type] = agent
        # 订阅相关主题
        self.message_bus.subscribe(f"to_{agent_type}", agent.receive_message)
        logger.info(f"✅ 注册Agent: {agent_type}")
        
    def dispatch_task(self, task: Dict) -> str:
        """分发任务"""
        target = task.get('target', 'pm')
        task_id = self.task_queue.add_task(task)
        
        # 通过消息总线发送
        self.message_bus.publish(f"to_{target}", {
            'type': 'task',
            'task_id': task_id,
            'content': task
        })
        
        return task_id
        
    def broadcast(self, message: Dict) -> None:
        """广播消息给所有Agent"""
        for agent_type in self.agents:
            self.message_bus.publish(f"to_{agent_type}", message)
            
    def get_company_status(self) -> Dict:
        """获取公司状态"""
        return {
            'timestamp': datetime.now().isoformat(),
            'agents': {name: agent.get_status() for name, agent in self.agents.items()},
            'pending_tasks': len(self.task_queue.tasks),
            'completed_tasks': len(self.task_queue.completed)
        }
        
    def start(self) -> None:
        """启动公司运转"""
        self.message_bus.start()
        logger.info("🏢 一人公司已启动运转")
        
    def stop(self) -> None:
        """停止公司运转"""
        self.message_bus.stop()
        # 保存所有Agent状态
        for agent in self.agents.values():
            agent.save_state()
        logger.info("🏢 一人公司已停止")
