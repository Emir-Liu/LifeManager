"""
请求拦截器
用于拦截和记录前端发送的HTTP请求
"""
import json
import asyncio
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class InterceptedRequest:
    """拦截的请求数据"""
    id: str
    method: str
    url: str
    headers: Dict
    request_data: Optional[Dict]
    response_status: int
    response_data: Optional[Dict]
    duration_ms: int
    timestamp: str
    success: bool


class RequestInterceptor:
    """请求拦截器"""

    def __init__(self):
        self.requests: List[InterceptedRequest] = []
        self.listeners: List[Callable] = []
        self._lock = asyncio.Lock()

    async def add_request(self, request: InterceptedRequest):
        """添加拦截的请求"""
        async with self._lock:
            self.requests.append(request)

        # 通知监听器
        for listener in self.listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(request)
                else:
                    listener(request)
            except Exception as e:
                print(f"监听器执行错误: {e}")

    def add_listener(self, listener: Callable):
        """添加请求监听器"""
        self.listeners.append(listener)

    def remove_listener(self, listener: Callable):
        """移除请求监听器"""
        if listener in self.listeners:
            self.listeners.remove(listener)

    def get_requests(self,
                     url_pattern: Optional[str] = None,
                     method: Optional[str] = None,
                     success_only: bool = False) -> List[InterceptedRequest]:
        """获取拦截的请求"""
        result = self.requests.copy()

        if url_pattern:
            result = [r for r in result if url_pattern in r.url]

        if method:
            result = [r for r in result if r.method.upper() == method.upper()]

        if success_only:
            result = [r for r in result if r.success]

        return result

    def get_last_request(self) -> Optional[InterceptedRequest]:
        """获取最后一个请求"""
        return self.requests[-1] if self.requests else None

    def clear(self):
        """清除所有请求记录"""
        self.requests.clear()

    def find_request(self,
                     url_pattern: Optional[str] = None,
                     method: Optional[str] = None,
                     timeout: int = 5) -> Optional[InterceptedRequest]:
        """
        查找符合条件的请求（阻塞式）
        用于验证某个请求是否被发送
        """
        import time
        start_time = time.time()

        while time.time() - start_time < timeout:
            requests = self.get_requests(url_pattern=url_pattern, method=method)
            if requests:
                return requests[-1]
            time.sleep(0.1)

        return None

    def to_dict(self) -> List[Dict]:
        """转换为字典列表"""
        return [asdict(r) for r in self.requests]

    def save_to_file(self, filepath: str):
        """保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    def load_from_file(self, filepath: str):
        """从文件加载"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.requests = [InterceptedRequest(**item) for item in data]


class RequestValidator:
    """请求验证器"""

    def __init__(self, interceptor: RequestInterceptor):
        self.interceptor = interceptor

    def validate_request_sent(self,
                              url_pattern: str,
                              method: Optional[str] = None,
                              expected_data: Optional[Dict] = None) -> tuple[bool, str]:
        """
        验证请求是否被发送
        返回: (是否通过, 错误信息)
        """
        requests = self.interceptor.get_requests(url_pattern=url_pattern, method=method)

        if not requests:
            return False, f"未找到匹配的请求: {url_pattern}"

        if expected_data:
            last_request = requests[-1]
            request_data = last_request.request_data or {}
            for key, value in expected_data.items():
                if key not in request_data or request_data[key] != value:
                    return False, f"请求数据不匹配: {key}={value}"

        return True, "验证通过"

    def validate_response_status(self,
                                  url_pattern: str,
                                  expected_status: int = 200) -> tuple[bool, str]:
        """验证响应状态码"""
        requests = self.interceptor.get_requests(url_pattern=url_pattern)

        if not requests:
            return False, f"未找到匹配的请求: {url_pattern}"

        last_request = requests[-1]
        if last_request.response_status != expected_status:
            return False, f"状态码不匹配: 期望 {expected_status}, 实际 {last_request.response_status}"

        return True, "验证通过"

    def validate_response_contains(self,
                                    url_pattern: str,
                                    key: str,
                                    expected_value: any) -> tuple[bool, str]:
        """验证响应数据包含特定值"""
        requests = self.interceptor.get_requests(url_pattern=url_pattern)

        if not requests:
            return False, f"未找到匹配的请求: {url_pattern}"

        last_request = requests[-1]
        response_data = last_request.response_data or {}

        if key not in response_data:
            return False, f"响应中不包含键: {key}"

        if response_data[key] != expected_value:
            return False, f"值不匹配: 期望 {expected_value}, 实际 {response_data[key]}"

        return True, "验证通过"
