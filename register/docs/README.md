# tavily-register

用于自动化 Tavily 账号注册、邮箱验证、登录与 API Key 获取的脚本集合，支持：

- 验证码识别（SVG → PNG → 视觉模型识别）
- GPTMail 临时邮箱流程
- 注册后自动获取/创建 API Key
- 浏览器指纹伪装（默认启用）
- 代理池（静态代理/API 代理、轮换与健康检查）

---

## 1. 项目概览

核心目标：尽可能自动化完成从“注册账号”到“拿到可用 Tavily Key”的全过程。

主流程由以下模块协作：

1. `scripts/batch_signup.py`：批量任务入口（CLI）
2. `tavily_register/core/register.py`：注册/登录/验证码/验证邮件/取 key 核心逻辑
3. `tavily_register/email/gptmail_client.py`：临时邮箱 API 客户端
4. `tavily_register/proxy/pool.py`：代理池管理（可选）
5. `tavily_register/utils/fingerprint.py`：浏览器指纹生成与注入

---

## 2. 目录结构

- `scripts/batch_signup.py`：批量注册与重试入口
- `tavily_register/core/register.py`：核心注册链路（requests.Session 驱动）
- `tavily_register/email/gptmail_client.py`：GPTMail API 封装
- `tavily_register/proxy/pool.py`：代理池核心实现
- `tavily_register/utils/fingerprint.py`：浏览器指纹实现
- `scripts/update_free_proxies.py`：免费代理更新脚本
- `docs/FINGERPRINT.md`：浏览器指纹说明
- `data/`：本地配置与运行输出
- `tests/`：pytest 测试

---

## 3. 环境要求

- Python `>= 3.12`
- 推荐使用 `uv` 进行依赖管理

依赖定义见 `pyproject.toml`，核心依赖包括：

- `requests`
- `svglib`
- `reportlab`
- `pyaml`
- `pysocks`

---

## 4. 安装

```bash
uv sync
```

如需直接运行脚本，建议统一使用：

```bash
uv run python <script>.py
```

---

## 5. 配置

### 5.1 创建 `data/config.yaml`

项目默认从 `data/config.yaml` 读取配置（已在 `.gitignore` 中忽略）。

可从 `docs/config.yaml.example` 复制：

```bash
copy docs\config.yaml.example data\config.yaml
```

示例：

```yaml
# OpenAI 兼容 Chat Completions（用于验证码识别）
OPENAI_BASEURL: "https://example.com/v1"
OPENAI_API_KEY: "YOUR_API_KEY"
OPENAI_MODEL: "YOUR_MODEL"

# 代理池（可选）
PROXY_POOL:
  enabled: false
  strategy: round-robin
  health_check: false
  health_check_timeout: 10
  providers:
    - type: static
      name: my-static-proxies
      proxies:
        - "http://proxy1.example.com:8080"
        - "http://user:pass@proxy2.example.com:8080"
```

### 5.2 GPTMail 相关参数

可通过命令行或环境变量设置：

- `GPTMAIL_BASE_URL`
- `GPTMAIL_API_KEY`
- `GPTMAIL_TIMEOUT`
- `GPTMAIL_PREFIX`
- `GPTMAIL_DOMAIN`

---

## 6. 快速开始

### 6.1 查看帮助

```bash
uv run python scripts/batch_signup.py --help
```

### 6.2 批量注册（自动生成邮箱）

```bash
uv run python scripts/batch_signup.py --count 5
```

### 6.3 指定邮箱列表注册

```bash
uv run python scripts/batch_signup.py --input emails.txt --count 1
```

> `--input` 存在时，实际按文件内容执行；`--count` 仅在无 `--input` 时生效。

### 6.4 重试失败记录

```bash
uv run python scripts/batch_signup.py --retry
```

### 6.5 禁用浏览器指纹（不推荐）

```bash
uv run python scripts/batch_signup.py --count 5 --no-fingerprint
```

---

## 7. 常用参数说明（`scripts/batch_signup.py`）

| 参数 | 说明 |
|---|---|
| `--retry` | 按 `data/failed.txt` 重试失败记录 |
| `--count`, `-n` | 注册数量（仅自动生成邮箱模式） |
| `--input`, `-i` | 输入邮箱文件（每行一个邮箱，支持 `email----...`） |
| `--output`, `-o` | 成功结果文件（默认 `data/api_keys.txt`） |
| `--failed` | 失败记录文件（默认 `data/failed.txt`） |
| `--banned-domains` | 禁用域名文件（默认 `data/banned_domains.txt`） |
| `--password` | 注册/登录密码 |
| `--interval` | 注册间隔秒数 |
| `--verify-timeout` | 验证邮件等待超时 |
| `--verify-interval` | 验证邮件轮询间隔 |
| `--debug-init` | 打印首次登录初始化接口调试信息 |
| `--no-fingerprint` | 关闭浏览器指纹 |
| `--proxy-enabled` / `--no-proxy` | 开关代理池（覆盖配置文件） |
| `--proxy-strategy` | 代理策略：`round-robin` / `random` |
| `--proxy-health-check` / `--no-proxy-health-check` | 开关代理健康检查 |

---

## 8. 验证码识别链路

验证码流程位于 `tavily_register/core/register.py`，关键步骤为：

1. 从注册页面提取 SVG base64
2. 将 SVG 转为 PNG（`svglib` + `reportlab`）
3. 调用 OpenAI 兼容视觉模型识别
4. 清洗识别结果（仅保留字母数字）
5. 提交注册表单并根据响应判断是否需要重试

若识别失败，优先检查：

- `OPENAI_BASEURL / OPENAI_API_KEY / OPENAI_MODEL` 是否正确
- 本地是否安装 `svglib`、`reportlab`
- 网络与代理是否稳定

---

## 9. 输出文件

默认输出：

- `data/api_keys.txt`：成功记录，格式 `email----api_key`
- `data/failed.txt`：失败记录，格式 `email----error`
- `data/banned_domains.txt`：被判定不可用的邮箱域名

---

## 10. 测试与验证

### 10.1 运行单元/属性测试

```bash
uv run python -m pytest tests -v
```

### 10.2 运行代理池相关测试

```bash
uv run python -m pytest tests/test_proxy_providers.py tests/test_properties.py tests/test_remaining.py -v
```

---

## 11. 代理池与扩展文档

- 免费代理来源：`docs/FREE_PROXY_SOURCES.md`
- 浏览器指纹说明：`docs/FINGERPRINT.md`

---

## 12. 常见问题

- `invalid-captcha`：验证码识别不准确，建议增加重试间隔、切换模型或优化代理。
- `ip-signup-blocked`：当前出口 IP 被限制，建议更换代理/网络。
- `custom-script-error-code_extensibility_error`：邮箱域名可能被封禁，程序会写入 `data/banned_domains.txt`。
- `获取验证码失败`：页面结构变化或网络异常导致未提取到验证码。
- 注册后无 key：脚本会尝试自动创建 key；若仍失败，检查 session 登录态与网络重试。

---

## 13. 合规与风险提示

本项目仅用于技术研究与测试。请在使用时遵守：

- 目标服务条款
- 当地法律法规
- 代理与邮箱服务商政策

请勿将脚本用于未经授权或滥用场景。
