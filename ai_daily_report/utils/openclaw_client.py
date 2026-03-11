#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 智能分析客户端
通过本地 OpenClaw Gateway 调用多模型进行深度分析

功能：
1. 调用 OpenClaw Gateway REST API
2. 支持多轮对话和上下文管理
3. 自动选择最优模型
4. 流式响应支持
"""

import os
import json
import requests
import subprocess
from typing import Optional, Dict, Any, List, Generator
from datetime import datetime


class OpenClawClient:
    """OpenClaw Gateway 客户端"""
    
    def __init__(
        self,
        gateway_url: str = "http://127.0.0.1:18789",
        auth_token: Optional[str] = None,
        timeout: int = 120
    ):
        """
        初始化 OpenClaw 客户端
        
        Args:
            gateway_url: OpenClaw Gateway 地址
            auth_token: 认证 Token（如未提供则从配置读取）
            timeout: 请求超时时间（秒）
        """
        self.gateway_url = gateway_url.rstrip('/')
        self.timeout = timeout
        self.auth_token = auth_token or self._get_auth_token()
        self.session_id = None
        
    def _get_auth_token(self) -> Optional[str]:
        """从 OpenClaw 配置文件读取 auth token"""
        config_path = os.path.expanduser("~/.openclaw/openclaw.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('gateway', {}).get('auth', {}).get('token')
        except Exception as e:
            print(f"读取 OpenClaw 配置失败: {e}")
        return None
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def check_gateway_status(self) -> Dict[str, Any]:
        """检查 Gateway 状态"""
        try:
            result = subprocess.run(
                ["openclaw", "status", "--json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return {"status": "running", "message": "Gateway 运行正常"}
            return {"status": "error", "message": result.stderr}
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Gateway 状态检查超时"}
        except FileNotFoundError:
            return {"status": "not_installed", "message": "OpenClaw 未安装"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def ensure_gateway_running(self) -> bool:
        """确保 Gateway 正在运行"""
        status = self.check_gateway_status()
        if status["status"] == "running":
            return True
        
        # 尝试启动 Gateway
        try:
            subprocess.run(
                ["openclaw", "gateway", "start"],
                capture_output=True,
                timeout=30
            )
            return True
        except Exception as e:
            print(f"启动 Gateway 失败: {e}")
            return False
    
    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        timeout: int = 120
    ) -> str:
        """
        发送聊天请求（通过 OpenClaw CLI）
        
        Args:
            message: 用户消息
            system_prompt: 系统提示词（会添加到消息前面）
            model: 指定模型（当前不支持，使用默认配置）
            temperature: 温度参数（当前不支持，使用默认配置）
            max_tokens: 最大 token 数（当前不支持，使用默认配置）
            stream: 是否流式返回（当前不支持）
            timeout: 超时时间（秒）
            
        Returns:
            模型响应文本
        """
        # 如果有系统提示词，添加到消息前面
        full_message = message
        if system_prompt:
            full_message = f"[系统指令：{system_prompt}]\n\n用户问题：{message}"
        
        try:
            # 使用 OpenClaw CLI 发送消息
            result = subprocess.run(
                [
                    "openclaw", "agent",
                    "--agent", "main",
                    "--message", full_message,
                    "--json",
                    "--timeout", str(timeout)
                ],
                capture_output=True,
                text=True,
                timeout=timeout + 10  # 给一点额外时间
            )
            
            if result.returncode == 0:
                try:
                    # 解析 JSON 输出
                    output = result.stdout.strip()
                    # 找到 JSON 部分（可能有其他输出）
                    json_start = output.find('{')
                    json_end = output.rfind('}') + 1
                    if json_start >= 0 and json_end > json_start:
                        data = json.loads(output[json_start:json_end])
                        
                        # 优先从 payloads 提取（OpenClaw 标准格式）
                        payloads = data.get("payloads", [])
                        if payloads and isinstance(payloads, list):
                            texts = [p.get("text", "") for p in payloads if p.get("text")]
                            if texts:
                                return "\n".join(texts)
                        
                        # 其他可能的字段
                        reply = data.get("reply", "") or data.get("content", "") or data.get("message", "")
                        if reply:
                            return reply
                        # 如果没有标准字段，尝试其他可能的字段
                        for key in ["text", "response", "output", "result"]:
                            if key in data and data[key]:
                                return str(data[key])
                except json.JSONDecodeError:
                    pass
                
                # 如果无法解析 JSON，返回原始输出
                return result.stdout.strip()
            else:
                print(f"OpenClaw CLI 错误: {result.stderr}")
                return ""
                
        except subprocess.TimeoutExpired:
            print(f"OpenClaw 请求超时（{timeout}秒）")
            return ""
        except FileNotFoundError:
            print("OpenClaw CLI 未安装，请运行: npm i -g openclaw")
            return ""
        except Exception as e:
            print(f"OpenClaw 请求失败: {e}")
            return ""
    
    def chat_simple(self, message: str, timeout: int = 60) -> str:
        """
        简单聊天（不使用 JSON 输出，更可靠）
        
        Args:
            message: 用户消息
            timeout: 超时时间
            
        Returns:
            响应文本
        """
        try:
            result = subprocess.run(
                ["openclaw", "agent", "--agent", "main", "--message", message],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                # 清理输出（移除 ANSI 颜色码和多余空白）
                output = result.stdout.strip()
                # 移除 ANSI 转义序列
                import re
                output = re.sub(r'\x1b\[[0-9;]*m', '', output)
                return output
            else:
                return ""
        except Exception as e:
            print(f"OpenClaw 简单聊天失败: {e}")
            return ""
    
    def _handle_stream_response(self, response) -> Generator[str, None, None]:
        """处理流式响应"""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
    
    def analyze_news(
        self,
        news_list: List[Dict],
        analysis_type: str = "comprehensive",
        expert_role: str = "AI行业专家"
    ) -> Dict[str, Any]:
        """
        分析新闻列表
        
        Args:
            news_list: 新闻列表
            analysis_type: 分析类型 (comprehensive/trend/impact/opportunity)
            expert_role: 专家角色
            
        Returns:
            分析结果
        """
        # 构建分析提示词
        system_prompt = f"""你是一位资深的{expert_role}，拥有20年以上行业经验。
你的任务是分析以下新闻，提供专业、深入的见解。

分析要求：
1. 识别关键趋势和重要信号
2. 评估对行业的潜在影响
3. 发现创业和投资机会
4. 提供可执行的建议

输出格式：JSON
{{
    "key_insights": ["关键洞察1", "关键洞察2", ...],
    "trends": ["趋势1", "趋势2", ...],
    "opportunities": ["机会1", "机会2", ...],
    "risks": ["风险1", "风险2", ...],
    "recommendations": ["建议1", "建议2", ...],
    "summary": "整体总结（200字以内）"
}}
"""
        
        # 格式化新闻内容
        news_text = "\n\n".join([
            f"标题: {n.get('title', '')}\n来源: {n.get('source', '')}\n摘要: {n.get('description', '')}"
            for n in news_list[:20]  # 限制数量避免超长
        ])
        
        user_message = f"请分析以下{len(news_list)}条新闻（展示前20条）：\n\n{news_text}"
        
        response = self.chat(
            message=user_message,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=4096
        )
        
        # 尝试解析 JSON 响应
        try:
            # 提取 JSON 部分
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response
            
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {
                "raw_response": response,
                "parse_error": True
            }
    
    def generate_expert_commentary(
        self,
        topic: str,
        context: str,
        expert_type: str = "行业分析师"
    ) -> str:
        """
        生成专家点评
        
        Args:
            topic: 主题
            context: 上下文信息
            expert_type: 专家类型
            
        Returns:
            专家点评文本
        """
        system_prompt = f"""你是一位{expert_type}，请针对给定主题提供专业点评。
要求：
- 观点犀利、有见地
- 结合行业趋势
- 给出可执行建议
- 控制在200字以内
"""
        
        response = self.chat(
            message=f"主题：{topic}\n\n背景信息：{context}\n\n请提供你的专业点评。",
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        return response
    
    def summarize_for_push(
        self,
        content: str,
        max_length: int = 2000,
        platform: str = "wecom"
    ) -> str:
        """
        为推送平台生成摘要
        
        Args:
            content: 原始内容
            max_length: 最大字符数
            platform: 推送平台 (wecom/email/telegram)
            
        Returns:
            适合推送的摘要
        """
        platform_hints = {
            "wecom": "企业微信群消息，支持 Markdown，需要简洁有力",
            "email": "邮件正文，可以稍微详细，支持 HTML 格式",
            "telegram": "Telegram 消息，支持 Markdown，注意表情符号的使用"
        }
        
        system_prompt = f"""将以下内容压缩为{max_length}字符以内的摘要。
平台: {platform_hints.get(platform, platform)}
要求:
- 保留最重要的信息
- 使用符合平台风格的格式
- 突出关键数据和结论
"""
        
        response = self.chat(
            message=content,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=max_length // 2
        )
        
        return response[:max_length]


class OpenClawAnalyzer:
    """基于 OpenClaw 的智能分析器"""
    
    def __init__(self):
        self.client = OpenClawClient()
        self.available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """检查 OpenClaw 是否可用"""
        status = self.client.check_gateway_status()
        return status["status"] == "running"
    
    def enhance_daily_report(
        self,
        news_data: List[Dict],
        report_type: str = "ai"
    ) -> Dict[str, Any]:
        """
        增强日报内容
        
        Args:
            news_data: 新闻数据
            report_type: 报告类型 (ai/retail)
            
        Returns:
            增强后的分析结果
        """
        if not self.available:
            return {"error": "OpenClaw 不可用", "enhanced": False}
        
        expert_roles = {
            "ai": "人工智能行业专家、技术趋势分析师",
            "retail": "零售行业专家、消费市场分析师"
        }
        
        # 分析新闻
        analysis = self.client.analyze_news(
            news_list=news_data,
            expert_role=expert_roles.get(report_type, "行业专家")
        )
        
        # 生成专家点评
        if not analysis.get("parse_error"):
            expert_comment = self.client.generate_expert_commentary(
                topic=f"今日{report_type.upper()}行业动态",
                context=analysis.get("summary", ""),
                expert_type=expert_roles.get(report_type, "行业专家")
            )
            analysis["expert_comment"] = expert_comment
        
        analysis["enhanced"] = True
        analysis["timestamp"] = datetime.now().isoformat()
        
        return analysis


# 便捷函数
def get_openclaw_client() -> OpenClawClient:
    """获取 OpenClaw 客户端实例"""
    return OpenClawClient()


def quick_analyze(text: str, expert_type: str = "分析师") -> str:
    """快速分析文本"""
    client = OpenClawClient()
    return client.chat(
        message=text,
        system_prompt=f"你是一位{expert_type}，请分析以下内容并给出专业见解。",
        temperature=0.7
    )


if __name__ == "__main__":
    # 测试代码
    client = OpenClawClient()
    
    print("检查 Gateway 状态...")
    status = client.check_gateway_status()
    print(f"状态: {status}")
    
    if status["status"] == "running":
        print("\n测试对话...")
        response = client.chat(
            message="请用一句话介绍今天AI领域最值得关注的趋势",
            system_prompt="你是一位AI行业专家",
            temperature=0.7
        )
        print(f"响应: {response}")
