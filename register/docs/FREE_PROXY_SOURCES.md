# 免费IP代理池资源

本文档整理了互联网上可用的免费IP代理池资源，帮助您快速配置代理池。

## ⚠️ 重要提示

**免费代理的局限性：**
- 稳定性较差，可能随时失效
- 速度较慢
- 安全性无法保证
- 可能被目标网站封禁
- 不适合生产环境

**建议：**
- 仅用于测试和开发
- 生产环境建议使用付费代理服务
- 定期更新代理列表
- 启用健康检查功能

## 📋 GitHub免费代理列表

### 1. Proxifly Free Proxy List
**更新频率：** 每5分钟  
**代理数量：** 2600+  
**支持类型：** HTTP, HTTPS, SOCKS4, SOCKS5  
**国家覆盖：** 74+

**直接下载链接：**
```
所有代理 (JSON): https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json
所有代理 (TXT): https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt
HTTP代理 (JSON): https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http/data.json
HTTPS代理 (JSON): https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/https/data.json
SOCKS5代理 (JSON): https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks5/data.json
```

**GitHub仓库：** https://github.com/proxifly/free-proxy-list

### 2. jetkai/proxy-list
**更新频率：** 每小时  
**支持类型：** HTTP, HTTPS, SOCKS4, SOCKS5  
**格式：** JSON, TXT, CSV, XML, YAML

**直接下载链接：**
```
在线代理 (TXT): https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt
在线代理 (JSON): https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/json/proxies.json
HTTP代理: https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt
SOCKS5代理: https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt
```

**GitHub仓库：** https://github.com/jetkai/proxy-list

### 3. monosans/proxy-list
**更新频率：** 每小时  
**特点：** 包含地理位置信息

**直接下载链接：**
```
HTTP代理: https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt
SOCKS4代理: https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt
SOCKS5代理: https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt
```

**GitHub仓库：** https://github.com/monosans/proxy-list

### 4. TheSpeedX/PROXY-List
**更新频率：** 每天  
**特点：** 简单易用

**直接下载链接：**
```
HTTP代理: https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt
SOCKS4代理: https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt
SOCKS5代理: https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt
```

**GitHub仓库：** https://github.com/TheSpeedX/PROXY-List

### 5. mmpx12/proxy-list
**更新频率：** 每小时  
**特点：** 包含VPN和Tor出口节点

**直接下载链接：**
```
HTTP代理: https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt
HTTPS代理: https://raw.githubusercontent.com/mmpx12/proxy-list/master/https.txt
SOCKS4代理: https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt
SOCKS5代理: https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt
```

**GitHub仓库：** https://github.com/mmpx12/proxy-list

## 🔌 免费代理API服务

### 1. Proxifly API
**免费额度：** 有限制  
**API端点：** https://api.proxifly.dev/get-proxy

**示例请求：**
```bash
curl -d '{"apiKey": "your_api_key", "country": ["US"], "https": true, "quantity": 10}' \
  -H 'Content-Type: application/json' \
  https://api.proxifly.dev/get-proxy
```

**网站：** https://proxifly.dev/

### 2. PubProxy
**免费额度：** 每次1-5个代理  
**API端点：** http://pubproxy.com/api/proxy

**示例请求：**
```bash
# 获取1个代理
curl http://pubproxy.com/api/proxy

# 获取5个代理
curl http://pubproxy.com/api/proxy?limit=5

# 获取美国代理
curl http://pubproxy.com/api/proxy?country=US

# 获取HTTPS代理
curl http://pubproxy.com/api/proxy?https=true
```

**网站：** http://pubproxy.com/

### 3. GetProxyList
**免费额度：** 有限制  
**API端点：** http://getproxylist.com/api/proxy

**特点：** RESTful API，返回JSON格式

**网站：** http://getproxylist.com/

### 4. Proxy-Free.com
**免费额度：** 10次请求/天  
**API端点：** https://proxy-free.com/free-api/proxies/

**网站：** https://proxy-free.com/free-proxy-api/

## 💡 使用方法

### 方法1: 从GitHub下载代理列表

创建一个Python脚本自动下载和更新代理列表：

```python
import requests

def download_proxy_list(url):
    """从GitHub下载代理列表"""
    response = requests.get(url)
    if response.status_code == 200:
        proxies = response.text.strip().split('\n')
        return [p.strip() for p in proxies if p.strip()]
    return []

# 下载HTTP代理
http_proxies = download_proxy_list(
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'
)

print(f"下载了 {len(http_proxies)} 个HTTP代理")
for proxy in http_proxies[:5]:
    print(f"  {proxy}")
```

### 方法2: 配置到代理池

在 `data/config.yaml` 中配置：

```yaml
PROXY_POOL:
  enabled: true
  strategy: round-robin
  health_check: true  # 建议启用健康检查
  health_check_timeout: 5
  
  providers:
    - type: static
      name: github-free-proxies
      proxies:
        # 从GitHub下载的代理列表
        - "proxy1.example.com:8080"
        - "proxy2.example.com:8080"
        - "proxy3.example.com:8080"
```

### 方法3: 创建自动更新脚本

创建 `scripts/update_free_proxies.py` 脚本：

```python
import requests
import yaml

def fetch_free_proxies():
    """从多个源获取免费代理"""
    sources = [
        'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
        'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
        'https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt',
    ]
    
    all_proxies = []
    for source in sources:
        try:
            response = requests.get(source, timeout=10)
            if response.status_code == 200:
                proxies = response.text.strip().split('\n')
                all_proxies.extend([p.strip() for p in proxies if p.strip()])
        except Exception as e:
            print(f"获取代理失败 {source}: {e}")
    
    # 去重
    return list(set(all_proxies))

def update_config(proxies):
    """更新配置文件"""
    with open('data/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if 'PROXY_POOL' not in config:
        config['PROXY_POOL'] = {}
    
    if 'providers' not in config['PROXY_POOL']:
        config['PROXY_POOL']['providers'] = []
    
    # 更新或添加免费代理供应商
    free_provider = {
        'type': 'static',
        'name': 'auto-updated-free-proxies',
        'proxies': proxies[:100]  # 限制数量
    }
    
    # 查找并更新现有的免费代理供应商
    found = False
    for i, provider in enumerate(config['PROXY_POOL']['providers']):
        if provider.get('name') == 'auto-updated-free-proxies':
            config['PROXY_POOL']['providers'][i] = free_provider
            found = True
            break
    
    if not found:
        config['PROXY_POOL']['providers'].append(free_provider)
    
    with open('data/config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)
    
    print(f"已更新 {len(proxies[:100])} 个代理到配置文件")

if __name__ == '__main__':
    proxies = fetch_free_proxies()
    print(f"获取到 {len(proxies)} 个代理")
    update_config(proxies)
```

运行脚本：
```bash
uv run python scripts/update_free_proxies.py
```

### 方法4: 使用定时任务自动更新

**Linux/Mac (crontab):**
```bash
# 每小时更新一次代理列表
0 * * * * cd /path/to/project && uv run python scripts/update_free_proxies.py
```

**Windows (任务计划程序):**
创建一个批处理文件 `update_proxies.bat`:
```batch
@echo off
cd /d "C:\path\to\project"
uv run python scripts/update_free_proxies.py
```

然后在任务计划程序中设置每小时运行一次。

## 🎯 推荐配置

### 测试环境配置

```yaml
PROXY_POOL:
  enabled: true
  strategy: random  # 随机选择，避免过度使用单个代理
  health_check: true  # 必须启用健康检查
  health_check_timeout: 5  # 较短的超时时间
  
  providers:
    - type: static
      name: free-proxies
      proxies:
        # 从GitHub自动更新的代理列表
        - "proxy1.com:8080"
        - "proxy2.com:8080"
```

### 生产环境配置（付费代理）

```yaml
PROXY_POOL:
  enabled: true
  strategy: round-robin
  health_check: true
  health_check_timeout: 10
  
  providers:
    # 付费代理服务（推荐）
    - type: api
      name: premium-proxy-service
      api_url: "https://api.premium-proxy.com/get"
      api_key: "your-premium-api-key"
      cache_size: 20
    
    # 备用免费代理（仅作后备）
    - type: static
      name: backup-free-proxies
      proxies:
        - "backup-proxy1.com:8080"
        - "backup-proxy2.com:8080"
```

## 📊 代理质量对比

| 来源 | 更新频率 | 数量 | 稳定性 | 速度 | 推荐度 |
|------|---------|------|--------|------|--------|
| Proxifly | 5分钟 | 2600+ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| jetkai | 1小时 | 1000+ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| monosans | 1小时 | 500+ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| TheSpeedX | 1天 | 300+ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| mmpx12 | 1小时 | 400+ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |

## 🔧 故障排查

### 问题1: 所有代理都无法连接

**解决方案：**
1. 启用健康检查：`health_check: true`
2. 减少超时时间：`health_check_timeout: 5`
3. 更新代理列表（运行 `scripts/update_free_proxies.py`）
4. 尝试不同的代理源

### 问题2: 代理速度太慢

**解决方案：**
1. 减少健康检查超时时间
2. 使用地理位置更近的代理
3. 考虑使用付费代理服务
4. 启用随机策略，避免过度使用单个代理

### 问题3: 频繁被目标网站封禁

**解决方案：**
1. 增加请求间隔
2. 使用更多代理轮换
3. 启用浏览器指纹功能
4. 考虑使用住宅代理（付费）

## 💰 付费代理服务推荐

如果免费代理无法满足需求，建议考虑以下付费服务：

1. **Bright Data (Luminati)** - 最大的代理网络
2. **Smartproxy** - 性价比高
3. **Oxylabs** - 企业级服务
4. **ProxyMesh** - 简单易用
5. **ScraperAPI** - 专为爬虫优化

## 📚 相关资源

- [配置文件示例](config.yaml.example)
- [代理池核心实现](../tavily_register/proxy/pool.py)
- [自动更新脚本](../scripts/update_free_proxies.py)

## ⚖️ 法律声明

使用代理时请遵守：
- 目标网站的服务条款
- 当地法律法规
- 代理服务提供商的使用政策

**免责声明：** 本文档仅供学习和研究使用，使用者需自行承担使用代理的风险和责任。
