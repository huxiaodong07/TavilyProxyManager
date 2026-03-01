# 浏览器指纹功能快速开始

## 🎯 一分钟了解

浏览器指纹功能可以让每个注册账号看起来像来自不同的真实用户,减少被 Tavily 风控系统检测的概率。

## ✨ 核心优势

- ✅ **自动启用**: 无需任何配置,默认开启
- ✅ **真实指纹**: 所有参数来自真实设备
- ✅ **独特性**: 每个邮箱使用不同的指纹
- ✅ **一致性**: 同一邮箱多次使用相同指纹
- ✅ **零性能损耗**: 对注册速度无影响

## 🚀 立即使用

### 方式 1: 默认使用 (推荐)

```bash
# 指纹功能默认启用,直接运行即可
uv run python batch_signup.py --count 3
```

运行时会看到:
```
============================================================
Tavily 批量注册
============================================================
输出文件: api_keys.txt
失败记录: failed.txt
浏览器指纹: 启用  ← 已启用

注册尝试 1/3
============================================================
    使用浏览器指纹: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...
```

### 方式 2: 禁用指纹 (不推荐)

```bash
# 如果遇到问题,可以临时禁用
uv run python batch_signup.py --count 3 --no-fingerprint
```

## 📊 指纹包含什么?

每个指纹包含 20+ 个真实浏览器特征:

| 特征 | 示例 |
|------|------|
| User-Agent | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.6367.60` |
| 操作系统 | Windows 11, macOS 13.5, Linux |
| 屏幕分辨率 | 1920x1080, 2560x1440 |
| WebGL 显卡 | NVIDIA RTX 3060, AMD RX 6700 XT |
| CPU 核心数 | 4, 8, 16 核 |
| 内存大小 | 8GB, 16GB, 32GB |
| 时区 | America/New_York, Asia/Shanghai |
| 语言 | en-US, zh-CN |

## 🔍 验证指纹工作

### 测试 1: 查看生成的指纹

```bash
python browser_fingerprint.py
```

输出:
```
=== 测试浏览器指纹生成 ===

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...

完整请求头:
  User-Agent: ...
  Accept-Language: en-US,en;q=0.9
  sec-ch-ua: "Chromium";v="124", "Google Chrome";v="124"
  ...

完整指纹数据:
{
  "platform": "Windows",
  "screenResolution": "1920x1080",
  "hardwareConcurrency": 8,
  "webglVendor": "Google Inc. (NVIDIA)",
  "webglRenderer": "ANGLE (NVIDIA GeForce RTX 3060...)",
  ...
}

=== 测试指纹一致性 ===
相同邮箱两次生成的 User-Agent 是否一致: True ✓
```

### 测试 2: 实际注册时观察

运行注册时,注意这一行:
```
    使用浏览器指纹: Mozilla/5.0 (Windows NT 10.0; Win64; x64)...
```

每次注册会显示不同的 User-Agent,说明指纹正在工作。

## 💡 常见问题

### Q1: 指纹会保存吗?
**A**: 当前版本存储在内存中,程序重启后会重新生成。但同一邮箱在同一次运行中会使用相同指纹。

### Q2: 指纹能完全避免风控吗?
**A**: 不能。指纹只是降低风控概率,还需要注意:
- IP 限制 (同一 IP 限制 5 个账号)
- 注册间隔 (建议 5 秒以上)
- 邮箱域名 (避免使用黑名单域名)

### Q3: 指纹会影响性能吗?
**A**: 几乎没有影响。生成一个指纹只需 < 1ms,内存占用 < 2KB。

### Q4: 如何知道指纹是否生效?
**A**: 
1. 运行时会显示 "浏览器指纹: 启用"
2. 每次注册会显示使用的 User-Agent
3. 不同邮箱会显示不同的 User-Agent

### Q5: 什么时候需要禁用指纹?
**A**: 
- 调试问题时,想排除指纹因素
- 发现指纹导致注册失败 (极少见)
- 使用 `--no-fingerprint` 参数即可

## 📈 效果对比

### 不使用指纹
```
所有请求使用相同的 User-Agent
→ 容易被识别为批量注册
→ 风控概率: 高
```

### 使用指纹
```
每个邮箱使用不同的 User-Agent + WebGL + Canvas 等
→ 看起来像不同的真实用户
→ 风控概率: 低
```

## 🎓 进阶使用

### 查看完整指纹数据

```python
from browser_fingerprint import get_fingerprint_for_email
import json

# 获取指定邮箱的指纹
fp = get_fingerprint_for_email("test@example.com")

# 查看完整数据
print(json.dumps(fp.get_fingerprint_data(), indent=2))
```

### 自定义指纹 (未来功能)

```python
# 计划支持
fp = BrowserFingerprint(
    os="Windows",
    chrome_version="124.0.6367.60",
    screen_resolution=(1920, 1080)
)
```

## 📚 更多信息

- 详细文档: [FINGERPRINT.md](FINGERPRINT.md)
- 更新日志: [CHANGELOG_FINGERPRINT.md](CHANGELOG_FINGERPRINT.md)
- 项目主页: [README.md](README.md)

## 🎉 开始使用

现在就试试吧!

```bash
# 注册 3 个账号,自动使用浏览器指纹
uv run python batch_signup.py --count 3
```

祝你注册顺利! 🚀
