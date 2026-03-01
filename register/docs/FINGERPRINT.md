# 浏览器指纹功能说明

## 功能概述

为了减少 Tavily 的风控检测,项目新增了浏览器指纹功能。该功能会为每个注册账号生成独特但真实的浏览器指纹,模拟真实用户行为。

## 指纹包含的信息

### 1. HTTP 请求头
- **User-Agent**: 随机但真实的浏览器版本
- **Accept-Language**: 随机语言偏好
- **sec-ch-ua**: Chrome 客户端提示
- **DNT**: Do Not Track 设置
- **Sec-Fetch-*** 系列头

### 2. 浏览器特征
- **操作系统**: Windows 10/11, macOS, Linux
- **Chrome 版本**: 120-124 最新版本
- **屏幕分辨率**: 常见分辨率 (1920x1080, 2560x1440 等)
- **硬件并发数**: CPU 核心数 (4-16)
- **设备内存**: RAM 大小 (4-32 GB)

### 3. WebGL 指纹
- **WebGL Vendor**: NVIDIA, Intel, AMD, Apple
- **WebGL Renderer**: 真实显卡型号
- 示例: `ANGLE (NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)`

### 4. Canvas/Audio 指纹
- **Canvas Noise**: 随机噪声值
- **Audio Noise**: 音频指纹噪声

### 5. 其他特征
- **时区**: 随机时区 (美国/欧洲/亚洲)
- **字体列表**: 10-15 个常见字体
- **插件列表**: PDF Viewer 等
- **存储支持**: localStorage, sessionStorage, indexedDB

## 使用方法

### 默认启用 (推荐)

```bash
# 浏览器指纹功能默认启用
uv run python scripts/batch_signup.py --count 5
```

### 禁用指纹功能

```bash
# 如果需要禁用指纹功能
uv run python scripts/batch_signup.py --count 5 --no-fingerprint
```

### 查看指纹信息

运行时会显示使用的 User-Agent:
```
注册尝试 1/3
============================================================
    使用浏览器指纹: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...
```

## 指纹一致性

- **相同邮箱 = 相同指纹**: 同一个邮箱地址在多次注册中会使用相同的指纹
- **不同邮箱 = 不同指纹**: 每个邮箱都有独特的指纹
- **种子机制**: 使用邮箱地址作为随机种子,确保可重现性

## 技术实现

### 核心文件

- `tavily_register/utils/fingerprint.py`: 指纹生成模块
  - `BrowserFingerprint`: 指纹生成器类
  - `get_fingerprint_for_email()`: 获取邮箱对应的指纹
  - `generate_random_fingerprint()`: 生成随机指纹

### 集成位置

- `tavily_register/core/register.py`:
  - `create_session()`: 创建带指纹的 session
  - `signup()`: 注册流程中使用指纹

- `scripts/batch_signup.py`:
  - 添加 `--no-fingerprint` 参数
  - 传递 `use_fingerprint` 参数到注册流程

## 测试指纹功能

```bash
# 运行批量注册（默认启用指纹）
uv run python scripts/batch_signup.py --count 1
```

输出示例:
```
=== 测试浏览器指纹生成 ===

User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...

完整请求头:
  User-Agent: ...
  Accept: ...
  Accept-Language: en-US,en;q=0.9
  ...

完整指纹数据:
{
  "userAgent": "...",
  "platform": "Windows",
  "screenResolution": "1920x1080",
  "hardwareConcurrency": 8,
  "webglVendor": "Google Inc. (NVIDIA)",
  ...
}

=== 测试指纹一致性 ===
相同邮箱两次生成的 User-Agent 是否一致: True
```

## 优势

1. **降低风控**: 每个账号使用不同的浏览器指纹,避免被识别为批量注册
2. **真实性**: 所有指纹参数都来自真实设备,不会触发异常检测
3. **一致性**: 同一账号多次操作使用相同指纹,行为更自然
4. **可配置**: 可以根据需要启用或禁用指纹功能

## 注意事项

1. 指纹功能不能完全避免风控,仍需注意:
   - IP 地址限制 (同一 IP 限制注册数量)
   - 注册间隔时间
   - 邮箱域名黑名单

2. 指纹数据存储在内存中,程序重启后会重新生成

3. 如果遇到问题,可以使用 `--no-fingerprint` 禁用该功能

## 未来改进

- [ ] 支持自定义指纹模板
- [ ] 指纹持久化存储
- [ ] 更多浏览器类型 (Firefox, Safari)
- [ ] 移动设备指纹
- [ ] TLS 指纹伪装
