"""
代理供应商单元测试
"""

import pytest
from unittest.mock import Mock, patch
from tavily_register.proxy.pool import APIProxyProvider, ProxyConfig


class TestAPIProxyProvider:
    """API代理供应商测试"""
    
    def test_api_provider_initialization(self):
        """测试API供应商初始化"""
        config = {
            "type": "api",
            "name": "test-api",
            "api_url": "https://api.example.com/proxy",
            "api_key": "test-key",
            "cache_size": 5
        }
        
        provider = APIProxyProvider(config)
        assert provider.name == "test-api"
        assert provider.api_url == "https://api.example.com/proxy"
        assert provider.api_key == "test-key"
        assert provider.cache_size == 5
        assert provider.cache == []
    
    def test_api_provider_uses_cache(self):
        """测试API供应商使用缓存"""
        config = {
            "type": "api",
            "name": "test-api",
            "api_url": "https://api.example.com/proxy"
        }
        
        provider = APIProxyProvider(config)
        
        # 手动添加缓存
        proxy1 = ProxyConfig(protocol="http", host="proxy1.com", port=8080)
        proxy2 = ProxyConfig(protocol="http", host="proxy2.com", port=8080)
        provider.cache = [proxy1, proxy2]
        
        # 获取代理应该从缓存中取
        result = provider.get_proxy()
        assert result == proxy1
        assert len(provider.cache) == 1
        assert provider.cache[0] == proxy2
    
    @patch('requests.get')
    def test_api_provider_fetches_from_api(self, mock_get):
        """测试从API获取代理"""
        config = {
            "type": "api",
            "name": "test-api",
            "api_url": "https://api.example.com/proxy",
            "api_key": "test-key"
        }
        
        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"host": "proxy1.com", "port": 8080, "protocol": "http"},
                {"host": "proxy2.com", "port": 8081, "protocol": "https"}
            ]
        }
        mock_get.return_value = mock_response
        
        provider = APIProxyProvider(config)
        proxy = provider.get_proxy()
        
        # 验证API被调用
        mock_get.assert_called_once()
        
        # 验证返回的代理
        assert proxy is not None
        assert proxy.host == "proxy1.com"
        assert proxy.port == 8080
        assert proxy.protocol == "http"
        
        # 验证缓存
        assert len(provider.cache) == 1
        assert provider.cache[0].host == "proxy2.com"
    
    def test_parse_api_response_list_format(self):
        """测试解析列表格式的API响应"""
        config = {"type": "api", "api_url": "https://api.example.com"}
        provider = APIProxyProvider(config)
        
        data = [
            {"host": "proxy1.com", "port": 8080},
            {"host": "proxy2.com", "port": 8081}
        ]
        
        proxies = provider._parse_api_response(data)
        assert len(proxies) == 2
        assert proxies[0].host == "proxy1.com"
        assert proxies[1].host == "proxy2.com"
    
    def test_parse_api_response_dict_format(self):
        """测试解析字典格式的API响应"""
        config = {"type": "api", "api_url": "https://api.example.com"}
        provider = APIProxyProvider(config)
        
        data = {
            "data": [
                {"host": "proxy1.com", "port": 8080},
                {"host": "proxy2.com", "port": 8081}
            ]
        }
        
        proxies = provider._parse_api_response(data)
        assert len(proxies) == 2
        assert proxies[0].host == "proxy1.com"
    
    def test_parse_api_item_string(self):
        """测试解析字符串格式的代理项"""
        config = {"type": "api", "api_url": "https://api.example.com"}
        provider = APIProxyProvider(config)
        
        proxy = provider._parse_api_item("proxy.com:8080")
        assert proxy is not None
        assert proxy.host == "proxy.com"
        assert proxy.port == 8080
    
    def test_parse_api_item_dict(self):
        """测试解析字典格式的代理项"""
        config = {"type": "api", "api_url": "https://api.example.com"}
        provider = APIProxyProvider(config)
        
        item = {
            "host": "proxy.com",
            "port": 8080,
            "protocol": "https",
            "username": "user",
            "password": "pass"
        }
        
        proxy = provider._parse_api_item(item)
        assert proxy is not None
        assert proxy.host == "proxy.com"
        assert proxy.port == 8080
        assert proxy.protocol == "https"
        assert proxy.username == "user"
        assert proxy.password == "pass"
    
    @patch('requests.get')
    def test_api_provider_handles_api_failure(self, mock_get):
        """测试API调用失败时的处理"""
        config = {
            "type": "api",
            "name": "test-api",
            "api_url": "https://api.example.com/proxy"
        }
        
        # 模拟API失败
        mock_get.side_effect = Exception("API Error")
        
        provider = APIProxyProvider(config)
        proxy = provider.get_proxy()
        
        # 应该返回None而不是抛出异常
        assert proxy is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
