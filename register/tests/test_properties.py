"""
基于属性的测试
使用Hypothesis进行属性测试
"""

from hypothesis import given, strategies as st, settings
import pytest
from tavily_register.proxy.pool import ProxyConfig, StaticProxyProvider, ProxyPool


# Feature: ip-proxy-pool, Property 3: 代理获取返回完整配置
@given(
    protocol=st.sampled_from(["http", "https"]),
    host=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=("L", "N"), 
        blacklist_characters=":/@ "
    )),
    port=st.integers(min_value=1, max_value=65535)
)
@settings(max_examples=100)
def test_proxy_config_completeness(protocol, host, port):
    """
    属性: 对于任意成功的代理获取操作，返回的ProxyConfig对象应该包含
    协议、主机、端口字段，且能够转换为有效的代理URL格式。
    
    验证: 需求 2.1, 2.2, 2.4
    """
    proxy = ProxyConfig(protocol=protocol, host=host, port=port)
    
    # 验证字段存在
    assert proxy.protocol == protocol
    assert proxy.host == host
    assert proxy.port == port
    
    # 验证能够转换为URL
    url = proxy.to_url()
    assert url.startswith(f"{protocol}://")
    assert host in url
    assert str(port) in url
    
    # 验证能够转换为requests proxies格式
    proxies = proxy.to_requests_proxies()
    assert isinstance(proxies, dict)
    assert "http" in proxies
    assert "https" in proxies
    assert proxies["http"] == url
    assert proxies["https"] == url


# Feature: ip-proxy-pool, Property 3: 代理获取返回完整配置（带认证）
@given(
    protocol=st.sampled_from(["http", "https"]),
    host=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@ "
    )),
    port=st.integers(min_value=1, max_value=65535),
    username=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@"
    )),
    password=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@"
    ))
)
@settings(max_examples=100)
def test_proxy_config_with_auth(protocol, host, port, username, password):
    """
    属性: 对于任意带认证信息的代理配置，应该正确包含用户名和密码，
    且URL格式正确。
    
    验证: 需求 2.1, 2.2, 2.4
    """
    proxy = ProxyConfig(
        protocol=protocol,
        host=host,
        port=port,
        username=username,
        password=password
    )
    
    # 验证字段存在
    assert proxy.protocol == protocol
    assert proxy.host == host
    assert proxy.port == port
    assert proxy.username == username
    assert proxy.password == password
    
    # 验证URL包含认证信息
    url = proxy.to_url()
    assert username in url
    assert password in url
    assert f"{protocol}://" in url
    assert f"@{host}:{port}" in url


if __name__ == "__main__":
    pytest.main([__file__, "-v"])



# Feature: ip-proxy-pool, Property 10: 健康检查准确性
@given(
    protocol=st.sampled_from(["http", "https"]),
    host=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@ "
    )),
    port=st.integers(min_value=1, max_value=65535)
)
@settings(max_examples=100, deadline=None)
def test_health_check_returns_boolean(protocol, host, port):
    """
    属性: 对于任意代理配置，health_check方法应该返回布尔值，
    不应该抛出异常。
    
    验证: 需求 6.2, 6.3
    """
    proxy = ProxyConfig(protocol=protocol, host=host, port=port)
    provider = StaticProxyProvider({"proxies": []})
    
    # health_check应该返回布尔值，不抛出异常
    result = provider.health_check(proxy, timeout=2)
    assert isinstance(result, bool)


# Feature: ip-proxy-pool, Property 10: 健康检查准确性（无效代理）
def test_health_check_invalid_proxy_returns_false():
    """
    属性: 对于明显无效的代理（如不存在的主机），health_check应该返回False。
    
    验证: 需求 6.2, 6.3
    """
    # 使用一个不存在的主机
    proxy = ProxyConfig(protocol="http", host="invalid-host-12345.com", port=8080)
    provider = StaticProxyProvider({"proxies": []})
    
    result = provider.health_check(proxy, timeout=2)
    assert result is False



# Feature: ip-proxy-pool, Property 7: 代理字符串解析正确性
@given(
    host=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@ "
    )),
    port=st.integers(min_value=1, max_value=65535)
)
@settings(max_examples=100)
def test_proxy_string_parsing_simple_format(host, port):
    """
    属性: 对于任意符合"host:port"格式的代理字符串，解析后应该
    正确提取主机和端口信息。
    
    验证: 需求 4.1
    """
    proxy_str = f"{host}:{port}"
    provider = StaticProxyProvider({"proxies": [proxy_str]})
    
    proxy = provider.get_proxy()
    assert proxy is not None
    assert proxy.host == host
    assert proxy.port == port
    assert proxy.protocol == "http"  # 默认协议


# Feature: ip-proxy-pool, Property 7: 代理字符串解析正确性（带认证）
@given(
    host=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@ "
    )),
    port=st.integers(min_value=1, max_value=65535),
    username=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@"
    )),
    password=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@"
    ))
)
@settings(max_examples=100)
def test_proxy_string_parsing_with_auth(host, port, username, password):
    """
    属性: 对于任意符合"host:port:username:password"格式的代理字符串，
    解析后应该正确提取所有信息。
    
    验证: 需求 4.1
    """
    proxy_str = f"{host}:{port}:{username}:{password}"
    provider = StaticProxyProvider({"proxies": [proxy_str]})
    
    proxy = provider.get_proxy()
    assert proxy is not None
    assert proxy.host == host
    assert proxy.port == port
    assert proxy.username == username
    assert proxy.password == password


# Feature: ip-proxy-pool, Property 7: 代理字符串解析正确性（URL格式）
@given(
    protocol=st.sampled_from(["http", "https"]),
    host=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@ "
    )),
    port=st.integers(min_value=1, max_value=65535)
)
@settings(max_examples=100)
def test_proxy_string_parsing_url_format(protocol, host, port):
    """
    属性: 对于任意符合"protocol://host:port"格式的代理字符串，
    解析后应该正确提取协议、主机和端口。
    
    验证: 需求 4.1
    """
    proxy_str = f"{protocol}://{host}:{port}"
    provider = StaticProxyProvider({"proxies": [proxy_str]})
    
    proxy = provider.get_proxy()
    assert proxy is not None
    assert proxy.protocol == protocol
    assert proxy.host == host
    assert proxy.port == port


# Feature: ip-proxy-pool, Property 7: 代理字符串解析正确性（完整URL格式）
@given(
    protocol=st.sampled_from(["http", "https"]),
    host=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@ "
    )),
    port=st.integers(min_value=1, max_value=65535),
    username=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@"
    )),
    password=st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=("L", "N"),
        blacklist_characters=":/@"
    ))
)
@settings(max_examples=100)
def test_proxy_string_parsing_full_url_format(protocol, host, port, username, password):
    """
    属性: 对于任意符合"protocol://username:password@host:port"格式的代理字符串，
    解析后应该正确提取所有信息。
    
    验证: 需求 4.1
    """
    proxy_str = f"{protocol}://{username}:{password}@{host}:{port}"
    provider = StaticProxyProvider({"proxies": [proxy_str]})
    
    proxy = provider.get_proxy()
    assert proxy is not None
    assert proxy.protocol == protocol
    assert proxy.host == host
    assert proxy.port == port
    assert proxy.username == username
    assert proxy.password == password



# Feature: ip-proxy-pool, Property 1: 配置加载完整性
@given(
    provider_count=st.integers(min_value=1, max_value=5),
    strategy=st.sampled_from(["round-robin", "random"])
)
@settings(max_examples=100)
def test_proxy_pool_config_loading(provider_count, strategy):
    """
    属性: 对于任意有效的代理池配置，加载后的ProxyPool对象应该包含
    配置中指定的所有供应商。
    
    验证: 需求 1.1, 1.2, 1.3
    """
    # 构造配置
    providers = []
    for i in range(provider_count):
        providers.append({
            "type": "static",
            "name": f"provider-{i}",
            "proxies": [f"proxy{i}.com:8080"]
        })
    
    config = {
        "enabled": True,
        "strategy": strategy,
        "providers": providers
    }
    
    pool = ProxyPool(config)
    
    # 验证配置正确加载
    assert pool.enabled is True
    assert pool.strategy == strategy
    assert len(pool.providers) == provider_count
    
    # 验证每个供应商都正确初始化
    for i, provider in enumerate(pool.providers):
        assert provider.name == f"provider-{i}"



# Feature: ip-proxy-pool, Property 2: 配置错误检测
def test_proxy_pool_handles_empty_providers():
    """
    属性: 当配置中没有供应商时，ProxyPool应该正常初始化但get_proxy返回None。
    
    验证: 需求 1.4
    """
    config = {
        "enabled": True,
        "providers": []
    }
    
    pool = ProxyPool(config)
    assert pool.enabled is True
    assert len(pool.providers) == 0
    
    # get_proxy应该返回None
    proxy = pool.get_proxy()
    assert proxy is None


def test_proxy_pool_handles_invalid_provider_type():
    """
    属性: 当配置中包含无效的供应商类型时，应该跳过该供应商并继续。
    
    验证: 需求 1.4
    """
    config = {
        "enabled": True,
        "providers": [
            {"type": "invalid_type", "name": "bad-provider"},
            {"type": "static", "name": "good-provider", "proxies": ["proxy.com:8080"]}
        ]
    }
    
    pool = ProxyPool(config)
    # 应该只初始化有效的供应商
    assert len(pool.providers) == 1
    assert pool.providers[0].name == "good-provider"



# Feature: ip-proxy-pool, Property 5: 轮询策略顺序性
def test_round_robin_strategy():
    """
    属性: 对于配置为round-robin策略的代理池，连续N次调用get_proxy
    应该依次返回每个供应商的代理。
    
    验证: 需求 3.2
    """
    config = {
        "enabled": True,
        "strategy": "round-robin",
        "providers": [
            {"type": "static", "name": "p1", "proxies": ["proxy1.com:8080"]},
            {"type": "static", "name": "p2", "proxies": ["proxy2.com:8080"]},
            {"type": "static", "name": "p3", "proxies": ["proxy3.com:8080"]}
        ]
    }
    
    pool = ProxyPool(config)
    
    # 连续获取代理，应该按顺序轮询
    proxies = [pool.get_proxy() for _ in range(6)]
    
    # 验证顺序
    assert proxies[0].host == "proxy1.com"
    assert proxies[1].host == "proxy2.com"
    assert proxies[2].host == "proxy3.com"
    assert proxies[3].host == "proxy1.com"  # 循环
    assert proxies[4].host == "proxy2.com"
    assert proxies[5].host == "proxy3.com"


# Feature: ip-proxy-pool, Property 6: 随机策略分布性
def test_random_strategy():
    """
    属性: 对于配置为random策略的代理池，大量调用get_proxy应该
    使每个供应商被选中的概率大致相等。
    
    验证: 需求 3.3
    """
    config = {
        "enabled": True,
        "strategy": "random",
        "providers": [
            {"type": "static", "name": "p1", "proxies": ["proxy1.com:8080"]},
            {"type": "static", "name": "p2", "proxies": ["proxy2.com:8080"]},
            {"type": "static", "name": "p3", "proxies": ["proxy3.com:8080"]}
        ]
    }
    
    pool = ProxyPool(config)
    
    # 大量获取代理
    counts = {"proxy1.com": 0, "proxy2.com": 0, "proxy3.com": 0}
    for _ in range(300):
        proxy = pool.get_proxy()
        counts[proxy.host] += 1
    
    # 验证分布大致均匀（每个应该在80-120之间，允许20%误差）
    for host, count in counts.items():
        assert 60 < count < 140, f"{host} count {count} not in expected range"
