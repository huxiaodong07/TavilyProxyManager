"""
剩余功能的快速测试
"""

import pytest
import json
import tempfile
import os
from tavily_register.proxy.pool import ProxyPool, ProxyConfig, StaticProxyProvider


# 任务6.1: 故障转移测试
def test_provider_failover():
    """测试供应商故障转移"""
    config = {
        "enabled": True,
        "providers": [
            {"type": "static", "name": "empty", "proxies": []},  # 空供应商
            {"type": "static", "name": "good", "proxies": ["proxy.com:8080"]}
        ]
    }
    
    pool = ProxyPool(config)
    proxy = pool.get_proxy()
    # 应该跳过空供应商，返回有效代理
    assert proxy is not None
    assert proxy.host == "proxy.com"


# 任务7.1: 统计功能测试
def test_statistics_recording():
    """测试统计信息记录"""
    config = {
        "enabled": True,
        "providers": [
            {"type": "static", "name": "p1", "proxies": ["proxy.com:8080"]}
        ]
    }
    
    pool = ProxyPool(config)
    proxy = pool.get_proxy()
    
    # 记录成功和失败
    pool.record_success(proxy)
    pool.record_success(proxy)
    pool.record_failure(proxy)
    
    stats = pool.get_stats()
    assert stats["success_count"] == 2
    assert stats["failure_count"] == 1
    assert stats["total_requests"] == 1  # get_proxy调用了一次


# 任务8.1: 统计持久化测试
def test_statistics_persistence():
    """测试统计信息保存和加载"""
    config = {
        "enabled": True,
        "providers": [
            {"type": "static", "name": "p1", "proxies": ["proxy.com:8080"]}
        ]
    }
    
    pool = ProxyPool(config)
    proxy = pool.get_proxy()
    pool.record_success(proxy)
    
    # 保存统计信息
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        json.dump(pool.get_stats(), f)
        temp_file = f.name
    
    try:
        # 读取统计信息
        with open(temp_file, 'r') as f:
            loaded_stats = json.load(f)
        
        # 验证数据一致
        assert loaded_stats["success_count"] == 1
        assert loaded_stats["total_requests"] == 1
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



# 任务10.1: 会话代理一致性测试
def test_session_proxy_consistency():
    """测试会话代理一致性"""
    from tavily_register.core.register import create_session
    
    config = {
        "enabled": True,
        "providers": [
            {"type": "static", "name": "p1", "proxies": ["proxy.com:8080"]}
        ]
    }
    
    pool = ProxyPool(config)
    session = create_session(proxy_pool=pool)
    
    # 验证代理已设置
    assert hasattr(session, 'proxy_config')
    assert session.proxy_config is not None
    assert session.proxies is not None
    
    # 验证代理一致性
    initial_proxy = session.proxy_config
    assert session.proxies["http"] == initial_proxy.to_url()
    assert session.proxies["https"] == initial_proxy.to_url()
