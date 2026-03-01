"""
自动从GitHub获取免费代理并更新配置文件
"""

import requests
import yaml
import os
import sys
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)


# 免费代理源列表
PROXY_SOURCES = [
    {
        'name': 'TheSpeedX HTTP',
        'url': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'type': 'http'
    },
    {
        'name': 'monosans HTTP',
        'url': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
        'type': 'http'
    },
    {
        'name': 'mmpx12 HTTP',
        'url': 'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt',
        'type': 'http'
    },
    {
        'name': 'jetkai HTTP',
        'url': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt',
        'type': 'http'
    },
]


def fetch_proxies_from_url(url, timeout=10):
    """
    从URL获取代理列表
    
    Args:
        url: 代理列表URL
        timeout: 超时时间（秒）
        
    Returns:
        代理列表
    """
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            proxies = response.text.strip().split('\n')
            # 过滤空行和注释
            return [p.strip() for p in proxies if p.strip() and not p.strip().startswith('#')]
        else:
            print(f"  ❌ 获取失败，状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"  ❌ 获取失败: {e}")
        return []


def fetch_all_free_proxies():
    """
    从所有源获取免费代理
    
    Returns:
        代理列表
    """
    print("=" * 60)
    print("开始获取免费代理...")
    print("=" * 60)
    
    all_proxies = []
    
    for source in PROXY_SOURCES:
        print(f"\n📥 正在获取: {source['name']}")
        print(f"   URL: {source['url']}")
        
        proxies = fetch_proxies_from_url(source['url'])
        if proxies:
            print(f"  ✅ 成功获取 {len(proxies)} 个代理")
            all_proxies.extend(proxies)
        else:
            print(f"  ⚠️  未获取到代理")
    
    # 去重
    unique_proxies = list(set(all_proxies))
    
    print(f"\n" + "=" * 60)
    print(f"总计获取: {len(all_proxies)} 个代理")
    print(f"去重后: {len(unique_proxies)} 个代理")
    print("=" * 60)
    
    return unique_proxies


def update_config_file(proxies, config_path=None, max_proxies=100):
    """
    更新配置文件中的代理列表
    
    Args:
        proxies: 代理列表
        config_path: 配置文件路径
        max_proxies: 最大代理数量
    """
    if config_path is None:
        config_path = os.path.join(DATA_DIR, 'config.yaml')

    print(f"\n📝 更新配置文件: {config_path}")
    
    # 读取现有配置
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {}
    
    # 确保PROXY_POOL配置存在
    if 'PROXY_POOL' not in config:
        config['PROXY_POOL'] = {
            'enabled': False,
            'strategy': 'round-robin',
            'health_check': True,
            'health_check_timeout': 5,
            'providers': []
        }
    
    if 'providers' not in config['PROXY_POOL']:
        config['PROXY_POOL']['providers'] = []
    
    # 限制代理数量
    limited_proxies = proxies[:max_proxies]
    
    # 创建或更新免费代理供应商
    free_provider = {
        'type': 'static',
        'name': 'auto-updated-free-proxies',
        'proxies': limited_proxies,
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # 查找并更新现有的免费代理供应商
    found = False
    for i, provider in enumerate(config['PROXY_POOL']['providers']):
        if provider.get('name') == 'auto-updated-free-proxies':
            config['PROXY_POOL']['providers'][i] = free_provider
            found = True
            print(f"  ✅ 已更新现有的免费代理供应商")
            break
    
    if not found:
        config['PROXY_POOL']['providers'].append(free_provider)
        print(f"  ✅ 已添加新的免费代理供应商")
    
    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
    
    print(f"  ✅ 已保存 {len(limited_proxies)} 个代理到配置文件")
    
    # 显示前5个代理作为示例
    print(f"\n📋 代理示例（前5个）:")
    for i, proxy in enumerate(limited_proxies[:5], 1):
        print(f"  {i}. {proxy}")
    
    if len(limited_proxies) > 5:
        print(f"  ... 还有 {len(limited_proxies) - 5} 个代理")


def save_proxy_list(proxies, output_file=None):
    """
    保存代理列表到文件
    
    Args:
        proxies: 代理列表
        output_file: 输出文件路径
    """
    if output_file is None:
        output_file = os.path.join(DATA_DIR, 'free_proxies.txt')

    print(f"\n💾 保存代理列表到: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 免费代理列表\n")
        f.write(f"# 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# 总数: {len(proxies)}\n")
        f.write(f"#\n")
        for proxy in proxies:
            f.write(f"{proxy}\n")
    
    print(f"  ✅ 已保存 {len(proxies)} 个代理")


def main():
    """主函数"""
    print("\n" + "🚀 " * 20)
    print("免费代理自动更新工具")
    print("🚀 " * 20 + "\n")
    
    # 获取免费代理
    proxies = fetch_all_free_proxies()
    
    if not proxies:
        print("\n❌ 未获取到任何代理，退出")
        return
    
    # 更新配置文件
    update_config_file(proxies, max_proxies=100)
    
    # 保存代理列表到文件
    save_proxy_list(proxies)
    
    print("\n" + "=" * 60)
    print("✅ 更新完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("  1. 在 data/config.yaml 中设置 PROXY_POOL.enabled: true 启用代理池")
    print("  2. 建议启用健康检查: PROXY_POOL.health_check: true")
    print("  3. 免费代理稳定性较差，建议定期运行此脚本更新")
    print("  4. 生产环境建议使用付费代理服务")
    print()


if __name__ == '__main__':
    main()
