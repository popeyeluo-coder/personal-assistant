"""
📋 项目管理专家 Agent
执行保障中心 - 保障项目完整落地，并可自我纠偏
"""

from typing import Dict, List, Any
from datetime import datetime
import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PMAgent(BaseAgent):
    """项目管理专家 - 确保所有任务高效落地"""
    
    def __init__(self, config_path: str = None):
        super().__init__('pm', config_path)
        
        self.projects = {}  # 项目列表
        self.tasks = []  # 任务列表
        self.milestones = []  # 里程碑
        self.issues = []  # 问题跟踪
        
    def process_task(self, task: Dict) -> Dict:
        task_type = task.get('content', {}).get('type', 'track_progress')
        handlers = {
            'create_project': self._create_project,
            'track_progress': self._track_progress,
            'manage_tasks': self._manage_tasks,
            'resolve_issues': self._resolve_issues,
            'generate_summary': self._generate_summary
        }
        return handlers.get(task_type, self._track_progress)(task)
    
    def _create_project(self, task: Dict) -> Dict:
        """创建项目"""
        project_info = task.get('content', {}).get('project', {})
        project = {
            'id': f"P{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'name': project_info.get('name', ''),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'milestones': [],
            'tasks': [],
            'progress': 0
        }
        self.projects[project['id']] = project
        return project
    
    def _track_progress(self, task: Dict) -> Dict:
        """跟踪进度"""
        return {
            'timestamp': datetime.now().isoformat(),
            'projects': {pid: {'progress': p['progress'], 'status': p['status']} 
                        for pid, p in self.projects.items()},
            'pending_tasks': len([t for t in self.tasks if t.get('status') == 'pending']),
            'blockers': self.issues,
            'next_milestones': self.milestones[:3]
        }
    
    def _manage_tasks(self, task: Dict) -> Dict:
        """管理任务"""
        action = task.get('content', {}).get('action', 'list')
        if action == 'create':
            new_task = task.get('content', {}).get('task', {})
            new_task['id'] = f"T{len(self.tasks)+1}"
            new_task['status'] = 'pending'
            new_task['created_at'] = datetime.now().isoformat()
            self.tasks.append(new_task)
            return new_task
        return {'tasks': self.tasks}
    
    def _resolve_issues(self, task: Dict) -> Dict:
        """解决问题"""
        issue = task.get('content', {}).get('issue', {})
        resolution = {
            'issue': issue,
            'analysis': '根因分析',
            'solution': '解决方案',
            'prevention': '预防措施'
        }
        return resolution
    
    def _generate_summary(self, task: Dict) -> Dict:
        """生成摘要"""
        period = task.get('content', {}).get('period', 'daily')
        return {
            'period': period,
            'timestamp': datetime.now().isoformat(),
            'completed': len([t for t in self.tasks if t.get('status') == 'completed']),
            'in_progress': len([t for t in self.tasks if t.get('status') == 'in_progress']),
            'blocked': len(self.issues),
            'highlights': [],
            'concerns': []
        }
    
    def daily_standup(self) -> Dict:
        """每日站会"""
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'yesterday': [],
            'today': [],
            'blockers': self.issues
        }
    
    def generate_report(self) -> str:
        return f"""
# 📋 项目管理报告
- 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
- 项目数: {len(self.projects)}
- 任务数: {len(self.tasks)}
- 问题数: {len(self.issues)}
---
*由项目管理专家 Agent 生成*
"""

def create_pm_agent(config_path: str = None) -> PMAgent:
    return PMAgent(config_path)
