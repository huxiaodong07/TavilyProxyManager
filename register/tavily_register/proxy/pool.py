"""
IP代理池模块
提供代理IP管理、轮换、健康检查和统计功能
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Optional
import requests
import yaml
import os


@dataclass
class ProxyConfig:
    """代理配置数据类"""
    protocol: str  # "http" 或 "https"
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    
    def to_url(self) -> str:
        """
        转换为代理URL格式
        
        Returns:
            代理URL字符串
        """
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"
    
    def to_requests_proxies(self) -> dict:
        """
        转换为requests库的proxies格式
        
        Returns:
            proxies字典，可直接用于requests
        """
        proxy_url = self.to_url()
        return {
            "http": proxy_url,
            "https": proxy_url
        }


def load_proxy_config(config_path: str = None) -> dict:
    """
    从配置文件加载代理池配置
    
    Args:
        config_path: 配置文件路径，默认为当前目录的config.yaml
        
    Returns:
        代理池配置字典，如果未配置则返回空字典
    """
    if config_path is None:
        config_path = os.path.abspath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "config.yaml")
        )
    
    if not os.path.exists(config_path):
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config.get("PROXY_POOL", {})


class ProxyProvider(ABC):
    """代理供应商抽象基类"""
    
    def __init__(self, config: dict):
        """
        初始化供应商
        
        Args:
            config: 供应商配置字典
        """
        self.config = config
        self.name = config.get("name", "unknown")
    
    @abstractmethod
    def get_proxy(self) -> Optional[ProxyConfig]:
        """
        获取一个代理
        
        Returns:
            ProxyConfig对象，失败返回None
        """
        pass
    
    @abstractmethod
    def release_proxy(self, proxy: ProxyConfig):
        """
        释放代理（可选实现，用于代理池回收）
        
        Args:
            proxy: 要释放的代理配置
        """
        pass
    
    def health_check(self, proxy: ProxyConfig, timeout: int = 10) -> bool:
        """
        检查代理健康状态
        
        Args:
            proxy: 要检查的代理
            timeout: 超时时间（秒）
            
        Returns:
            True表示健康，False表示不可用
        """
        test_url = "https://httpbin.org/ip"
        try:
            response = requests.get(
                test_url,
                proxies=proxy.to_requests_proxies(),
                timeout=timeout
            )
            return response.status_code == 200
        except Exception:
            return False


class StaticProxyProvider(ProxyProvider):
    """静态代理列表供应商"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.proxies = self._parse_proxy_list(config.get("proxies", []))
        self.current_index = 0
    
    def _parse_proxy_list(self, proxy_list: list) -> list:
        """
        解析代理列表
        
        支持格式:
        - "host:port"
        - "host:port:username:password"
        - "protocol://host:port"
        - "protocol://username:password@host:port"
        
        Args:
            proxy_list: 代理字符串列表
            
        Returns:
            ProxyConfig对象列表
        """
        configs = []
        for proxy_str in proxy_list:
            try:
                config = self._parse_proxy_string(proxy_str)
                if config:
                    configs.append(config)
            except Exception as e:
                print(f"警告: 解析代理失败 {proxy_str}: {e}")
        return configs
    
    def _parse_proxy_string(self, proxy_str: str) -> Optional[ProxyConfig]:
        """
        解析单个代理字符串
        
        Args:
            proxy_str: 代理字符串
            
        Returns:
            ProxyConfig对象，解析失败返回None
        """
        if not proxy_str or not isinstance(proxy_str, str):
            return None
        
        proxy_str = proxy_str.strip()
        
        # 格式1: protocol://username:password@host:port
        if "://" in proxy_str:
            parts = proxy_str.split("://", 1)
            protocol = parts[0]
            rest = parts[1]
            
            # 检查是否有认证信息
            if "@" in rest:
                auth_part, host_part = rest.rsplit("@", 1)
                if ":" in auth_part:
                    username, password = auth_part.split(":", 1)
                else:
                    username = auth_part
                    password = None
            else:
                username = None
                password = None
                host_part = rest
            
            # 解析host:port
            if ":" in host_part:
                host, port_str = host_part.rsplit(":", 1)
                try:
                    port = int(port_str)
                except ValueError:
                    return None
            else:
                return None
            
            return ProxyConfig(
                protocol=protocol,
                host=host,
                port=port,
                username=username,
                password=password
            )
        
        # 格式2: host:port:username:password 或 host:port
        parts = proxy_str.split(":")
        if len(parts) == 2:
            # host:port
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                return None
            return ProxyConfig(protocol="http", host=host, port=port)
        
        elif len(parts) == 4:
            # host:port:username:password
            host = parts[0]
            try:
                port = int(parts[1])
            except ValueError:
                return None
            username = parts[2]
            password = parts[3]
            return ProxyConfig(
                protocol="http",
                host=host,
                port=port,
                username=username,
                password=password
            )
        
        return None
    
    def get_proxy(self) -> Optional[ProxyConfig]:
        """
        轮询获取代理
        
        Returns:
            ProxyConfig对象，列表为空返回None
        """
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def release_proxy(self, proxy: ProxyConfig):
        """静态列表不需要释放"""
        pass


class APIProxyProvider(ProxyProvider):
    """API类型代理供应商"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.api_params = config.get("api_params", {})
        self.cache = []  # 缓存获取的代理
        self.cache_size = config.get("cache_size", 10)
    
    def get_proxy(self) -> Optional[ProxyConfig]:
        """
        从API获取代理
        
        Returns:
            ProxyConfig对象，失败返回None
        """
        # 优先使用缓存
        if self.cache:
            return self.cache.pop(0)
        
        # 从API获取新代理
        try:
            proxies = self._fetch_from_api()
            if proxies:
                self.cache.extend(proxies[1:])  # 缓存剩余代理
                return proxies[0]
        except Exception as e:
            print(f"从API获取代理失败: {e}")
        
        return None
    
    def _fetch_from_api(self) -> list:
        """
        从API获取代理列表
        
        Returns:
            ProxyConfig对象列表
        """
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        response = requests.get(
            self.api_url,
            headers=headers,
            params=self.api_params,
            timeout=30
        )
        response.raise_for_status()
        
        # 解析API响应
        data = response.json()
        return self._parse_api_response(data)
    
    def _parse_api_response(self, data: dict) -> list:
        """
        解析API响应数据
        
        Args:
            data: API响应的JSON数据
            
        Returns:
            ProxyConfig对象列表
        """
        # 通用格式解析
        proxies = []
        
        # 尝试多种常见的API响应格式
        if isinstance(data, list):
            # 格式1: 直接是代理列表
            for item in data:
                proxy = self._parse_api_item(item)
                if proxy:
                    proxies.append(proxy)
        
        elif isinstance(data, dict):
            # 格式2: {"data": [...]} 或 {"proxies": [...]}
            proxy_list = data.get("data") or data.get("proxies") or data.get("results")
            if proxy_list and isinstance(proxy_list, list):
                for item in proxy_list:
                    proxy = self._parse_api_item(item)
                    if proxy:
                        proxies.append(proxy)
        
        return proxies
    
    def _parse_api_item(self, item) -> Optional[ProxyConfig]:
        """
        解析单个API返回的代理项
        
        Args:
            item: 代理项（可能是字符串或字典）
            
        Returns:
            ProxyConfig对象，解析失败返回None
        """
        if isinstance(item, str):
            # 如果是字符串，使用StaticProxyProvider的解析方法
            parser = StaticProxyProvider({"proxies": []})
            return parser._parse_proxy_string(item)
        
        elif isinstance(item, dict):
            # 如果是字典，提取字段
            protocol = item.get("protocol", "http")
            host = item.get("host") or item.get("ip")
            port = item.get("port")
            username = item.get("username") or item.get("user")
            password = item.get("password") or item.get("pass")
            
            if host and port:
                try:
                    port = int(port)
                    return ProxyConfig(
                        protocol=protocol,
                        host=host,
                        port=port,
                        username=username,
                        password=password
                    )
                except (ValueError, TypeError):
                    pass
        
        return None
    
    def release_proxy(self, proxy: ProxyConfig):
        """API代理通常不需要显式释放"""
        pass


class ProxyPool:
    """代理池管理器"""
    
    def __init__(self, config: dict):
        """
        初始化代理池
        
        Args:
            config: 代理池配置
        """
        self.enabled = config.get("enabled", False)
        self.providers = self._init_providers(config.get("providers", []))
        self.strategy = config.get("strategy", "round-robin")  # round-robin 或 random
        self.current_provider_index = 0
        self.health_check_enabled = config.get("health_check", False)
        self.health_check_timeout = config.get("health_check_timeout", 10)
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "success_count": 0,
            "failure_count": 0,
            "proxy_usage": {}  # {proxy_url: {"success": 0, "failure": 0}}
        }
    
    def _init_providers(self, provider_configs: list) -> list:
        """
        初始化代理供应商
        
        Args:
            provider_configs: 供应商配置列表
            
        Returns:
            ProxyProvider对象列表
        """
        providers = []
        for config in provider_configs:
            provider_type = config.get("type")
            if provider_type == "static":
                providers.append(StaticProxyProvider(config))
            elif provider_type == "api":
                providers.append(APIProxyProvider(config))
            else:
                print(f"警告: 未知的供应商类型 {provider_type}")
        return providers
    
    def get_proxy(self) -> Optional[ProxyConfig]:
        """
        获取一个可用代理
        
        Returns:
            ProxyConfig对象，失败返回None
        """
        if not self.enabled or not self.providers:
            return None
        
        self.stats["total_requests"] += 1
        
        # 尝试从所有供应商获取代理（故障转移）
        attempts = 0
        max_attempts = len(self.providers) * 2  # 允许尝试所有供应商两轮
        
        while attempts < max_attempts:
            # 根据策略选择供应商
            if self.strategy == "random":
                import random
                provider = random.choice(self.providers)
            else:  # round-robin
                provider = self.providers[self.current_provider_index]
                self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
            
            # 获取代理
            proxy = provider.get_proxy()
            if not proxy:
                attempts += 1
                continue
            
            # 健康检查
            if self.health_check_enabled:
                if not provider.health_check(proxy, self.health_check_timeout):
                    print(f"代理健康检查失败: {proxy.to_url()}")
                    self.record_failure(proxy)
                    attempts += 1
                    continue
            
            return proxy
        
        # 所有供应商都失败
        return None
    
    def record_success(self, proxy: ProxyConfig):
        """
        记录代理使用成功
        
        Args:
            proxy: 使用的代理配置
        """
        self.stats["success_count"] += 1
        proxy_url = proxy.to_url()
        if proxy_url not in self.stats["proxy_usage"]:
            self.stats["proxy_usage"][proxy_url] = {"success": 0, "failure": 0}
        self.stats["proxy_usage"][proxy_url]["success"] += 1
    
    def record_failure(self, proxy: ProxyConfig):
        """
        记录代理使用失败
        
        Args:
            proxy: 使用的代理配置
        """
        self.stats["failure_count"] += 1
        proxy_url = proxy.to_url()
        if proxy_url not in self.stats["proxy_usage"]:
            self.stats["proxy_usage"][proxy_url] = {"success": 0, "failure": 0}
        self.stats["proxy_usage"][proxy_url]["failure"] += 1
    
    def get_stats(self) -> dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典的副本
        """
        return self.stats.copy()
    
    def print_stats(self):
        """打印统计信息"""
        print("\n" + "=" * 60)
        print("代理使用统计")
        print("=" * 60)
        print(f"总请求数: {self.stats['total_requests']}")
        print(f"成功: {self.stats['success_count']}")
        print(f"失败: {self.stats['failure_count']}")
        print("\n代理详情:")
        for proxy_url, usage in self.stats["proxy_usage"].items():
            print(f"  {proxy_url}")
            print(f"    成功: {usage['success']}, 失败: {usage['failure']}")
        print("=" * 60)
