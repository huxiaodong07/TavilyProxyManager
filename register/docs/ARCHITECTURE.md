# Tavily Register 项目架构文档

> 目标：让后续接手者在不通读全部源码的前提下，快速定位“入口、数据流、模块职责、常改点”。

---

## 1. 项目目标与边界

本项目用于自动化完成 Tavily 账号注册流程，核心能力包括：

1. 访问注册页并提取验证码（SVG）。
2. 将 SVG 转 PNG，并调用视觉模型识别验证码。
3. 提交注册、设置密码、等待验证邮件、完成邮箱验证。
4. 登录并获取/创建 API Key。
5. 支持批量处理、失败重试、邮箱域名封禁、代理池、浏览器指纹。

不包含：
- Web UI；
- 持久化数据库；
- 服务端 API（这是客户端自动化脚本项目）。

---

## 2. 顶层目录结构

```text
register/
├─ docs/                     # 全部文档
├─ scripts/                  # 全部可执行脚本入口
├─ tavily_register/          # 核心 Python 包（业务逻辑）
├─ tests/                    # 测试代码
├─ .gitignore
├─ .python-version
├─ pyproject.toml
└─ uv.lock
```

约定：
- 文档放 `docs/`
- 脚本放 `scripts/`
- 本地配置与运行产物放 `data/`（被 `.gitignore` 忽略，不在仓库内追踪）

`data/` 运行时常见文件：
- `data/config.yaml`
- `data/api_keys.txt`
- `data/failed.txt`
- `data/banned_domains.txt`
- `data/free_proxies.txt`

---

## 3. 运行入口（Entry Points）

### 3.1 批量注册主入口
- 文件：`scripts/batch_signup.py`
- 作用：CLI 调度批量注册与重试，串联邮箱、注册、验证、登录、取 key。

常用命令：
- `uv run python scripts/batch_signup.py --count 5`
- `uv run python scripts/batch_signup.py --retry`

### 3.2 免费代理更新入口
- 文件：`scripts/update_free_proxies.py`
- 作用：抓取公开代理源，更新 `data/config.yaml` 中 `PROXY_POOL.providers`，并输出 `data/free_proxies.txt`。

---

## 4. 模块依赖关系（从上到下）

```text
scripts/batch_signup.py
  ├─ tavily_register.core.register
  │    ├─ tavily_register.utils.fingerprint
  │    └─ requests / svglib / reportlab / (可选) playwright
  ├─ tavily_register.email.gptmail_client
  └─ tavily_register.proxy.pool

scripts/update_free_proxies.py
  └─ requests / yaml

tests/*
  └─ 直接测试 tavily_register.proxy.pool 与部分 core 行为
```

---

## 5. 端到端数据流

### 5.1 注册主流程数据流

1. `scripts/batch_signup.py` 读取参数和配置（默认 `data/config.yaml`）。
2. 生成或加载邮箱：
   - 自动生成：`GPTMailClient.generate_email()`
   - 指定输入：`--input` 文件加载
3. 执行 `signup()`：
   - 拉取注册页
   - 提取验证码 SVG
   - `recognize_captcha_with_vision()` 调视觉模型
   - 提交邮箱+验证码
   - 设置密码
4. 若注册成功但未得到 key：
   - 等验证邮件 `wait_for_verification_link()`
   - `verify_email()` 完成验证
   - `get_api_keys()` 获取 key；必要时 `create_api_key()`
5. 结果落盘：
   - 成功 `data/api_keys.txt`
   - 失败 `data/failed.txt`
   - 域名禁用 `data/banned_domains.txt`

### 5.2 验证码识别链路

1. 从 HTML 中提取 `data:image/svg+xml;base64,...`
2. `svg_to_png_base64()` 把 SVG 转 PNG
3. 组装 OpenAI 兼容 `chat/completions` 请求（视觉模型）
4. 解析 `choices[0].message.content`
5. 清洗为字母数字（去噪）
6. 返回验证码字符串给注册/登录提交流程

---

## 6. 文件级职责说明（逐文件）

> 下列为当前仓库可见文件。`data/` 为运行时目录，不计入 Git 追踪文件清单。

### 6.1 根目录文件

#### `pyproject.toml`
- 类型：项目元数据与依赖声明。
- 关键内容：
  - `requires-python >= 3.12`
  - 依赖：`requests`、`svglib`、`reportlab`、`pyaml`、`pysocks`
  - `readme = "docs/README.md"`
- 何时改：升级依赖、修改项目元信息。

#### `uv.lock`
- 类型：锁定依赖版本。
- 作用：保证团队/环境安装一致。
- 何时改：执行依赖更新后自动变化。

#### `.python-version`
- 类型：Python 版本提示。
- 作用：统一本地解释器版本。

#### `.gitignore`
- 类型：Git 忽略规则。
- 关键点：忽略 `data/config.yaml` 与运行产物（keys/failed/free_proxies 等）。

---

### 6.2 文档目录 `docs/`

#### `docs/README.md`
- 对外使用文档：安装、配置、命令、常见问题。
- 新人首读文件。

#### `docs/config.yaml.example`
- 配置模板：视觉模型与代理池示例结构。
- 新环境初始化时复制到 `data/config.yaml`。

#### `docs/FINGERPRINT.md`
- 浏览器指纹策略说明：设计动机、参数、使用方式。

#### `docs/FREE_PROXY_SOURCES.md`
- 免费代理来源、更新方式、风险提示。

#### `docs/ARCHITECTURE.md`（本文件）
- 架构与文件职责索引。
- 后续改动应同步更新。

---

### 6.3 脚本目录 `scripts/`

#### `scripts/batch_signup.py`
- 项目主调度脚本（CLI）。
- 主要职责：
  1. 解析命令参数。
  2. 加载配置、初始化代理池。
  3. 生成/读取邮箱并去重已注册账号。
  4. 调用核心注册流程并处理失败重试。
  5. 保存成功/失败结果到 `data/`。
- 关键函数：
  - `batch_signup()`：主流程。
  - `retry_failed()`：读取失败文件重试。
  - `try_login_get_key()`：注册失败后尝试登录拿 key。
  - `_verify_with_gptmail_and_get_key()`：邮件验证并获取 key。
- 输入：命令行参数、环境变量、`data/config.yaml`。
- 输出：`data/api_keys.txt`、`data/failed.txt`、`data/banned_domains.txt`。
- 常改点：
  - 注册策略（重试次数、间隔）
  - 输出格式
  - 错误码分支处理

#### `scripts/update_free_proxies.py`
- 代理更新工具。
- 主要职责：
  1. 拉取多个免费代理源。
  2. 去重并截断数量。
  3. 更新 `data/config.yaml` 的 `PROXY_POOL.providers`。
  4. 保存 `data/free_proxies.txt`。
- 关键函数：
  - `fetch_all_free_proxies()`
  - `update_config_file()`
  - `save_proxy_list()`
- 常改点：代理源 URL、过滤规则、最大代理数量。

---

### 6.4 核心包 `tavily_register/`

#### `tavily_register/core/register.py`
- 核心业务模块（最关键）。
- 主要职责：
  1. 加载配置 `load_config()`（默认 `data/config.yaml`）。
  2. 创建会话 `create_session()`（指纹 + 可选代理）。
  3. 注册页/验证码处理：`get_signup_page()`、`fetch_page_with_captcha()`。
  4. 验证码识别：`svg_to_png_base64()`、`recognize_captcha_with_vision()`。
  5. 注册提交：`submit_signup_step1()`、`submit_signup_password()`。
  6. 邮件验证：`verify_email()`。
  7. 登录与取 key：`login_after_verification()`、`get_api_keys()`、`create_api_key()`。
  8. 总编排：`signup()`。
- 关键输入：
  - 视觉模型配置（`OPENAI_BASEURL/KEY/MODEL`）
  - 用户邮箱/密码
  - 可选代理/指纹参数
- 关键输出：
  - 各步骤结果字典（含 `success/error/status_code/error_code`）
  - API key 列表或 key 对象
- 高风险改动区：
  - Auth0 表单字段提取逻辑
  - 验证码响应解析逻辑
  - `get_api_keys()` 的重试与创建策略

#### `tavily_register/email/gptmail_client.py`
- GPTMail API 客户端封装。
- 主要职责：
  - 统一请求封装 `_request()`。
  - 生成邮箱、列邮件、取邮件详情、删邮件。
  - 轮询邮箱并提取验证链接 `wait_for_verification_link()`。
- 关键类/函数：
  - `GPTMailClient`
  - `GPTMailAPIError`
- 常改点：API 返回结构适配、异常处理与重试策略。

#### `tavily_register/proxy/pool.py`
- 代理池子系统。
- 主要职责：
  - 代理配置模型 `ProxyConfig`
  - 供应商抽象 `ProxyProvider`
  - 静态供应商 `StaticProxyProvider`
  - API 供应商 `APIProxyProvider`
  - 池管理 `ProxyPool`（轮询/随机、健康检查、统计）
- 常改点：
  - 新增供应商类型
  - 健康检查地址与超时
  - 选择策略与统计维度

#### `tavily_register/utils/fingerprint.py`
- 浏览器指纹子系统。
- 主要职责：
  - 生成 UA、请求头、设备特征。
  - 通过邮箱种子保证同邮箱指纹稳定。
- 关键类/函数：
  - `BrowserFingerprint`
  - `FingerprintManager`
  - `get_fingerprint_for_email()`
- 常改点：指纹参数池、头部策略、伪装强度。

---

### 6.5 测试目录 `tests/`

#### `tests/test_proxy_providers.py`
- 侧重 `APIProxyProvider` 单元测试：初始化、缓存、API 拉取、解析容错。

#### `tests/test_properties.py`
- Hypothesis 属性测试：
  - 代理配置完整性
  - 字符串解析正确性
  - 健康检查返回值性质
  - 轮询/随机策略性质

#### `tests/test_remaining.py`
- 补充行为测试：
  - 供应商故障转移
  - 统计记录
  - 会话代理一致性

---

## 7. 配置与数据契约

### 7.1 `data/config.yaml`
核心字段：
- `OPENAI_BASEURL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `PROXY_POOL`
  - `enabled`
  - `strategy`: `round-robin` / `random`
  - `health_check`
  - `health_check_timeout`
  - `providers`: `static` / `api`

### 7.2 运行输出文件格式
- `data/api_keys.txt`
  - 行格式：`email----api_key`
- `data/failed.txt`
  - 行格式：`email----error`
- `data/banned_domains.txt`
  - 每行一个域名
- `data/free_proxies.txt`
  - 文本代理列表（含注释头）

---

## 8. 调试与排障定位图

### 8.1 验证码识别失败
优先看：
1. `tavily_register/core/register.py::recognize_captcha_with_vision`
2. `tavily_register/core/register.py::svg_to_png_base64`
3. `data/config.yaml` 中模型配置

### 8.2 注册页结构变化（提取不到字段）
优先看：
1. `extract_form_data()`
2. `_extract_primary_form_html()`
3. `_extract_action_value()`

### 8.3 验证邮件收不到/解析不到链接
优先看：
1. `tavily_register/email/gptmail_client.py::wait_for_verification_link`
2. 正则 patterns 是否需要更新
3. GPTMail API 的字段变更

### 8.4 已登录但拿不到 key
优先看：
1. `get_api_keys()`
2. `create_api_key()`
3. `run_first_login_init()`

### 8.5 代理相关异常
优先看：
1. `load_proxy_config()`
2. `ProxyPool.get_proxy()`
3. `StaticProxyProvider/APIProxyProvider` 的解析逻辑

---

## 9. 常见改动任务与文件落点

1. **改验证码模型/网关**
   - 改 `data/config.yaml`
   - 必要时改 `recognize_captcha_with_vision()`

2. **新增代理来源**
   - 改 `scripts/update_free_proxies.py::PROXY_SOURCES`

3. **新增代理供应商类型**
   - 改 `tavily_register/proxy/pool.py`（新增 Provider + `_init_providers` 注册）

4. **调整批量策略（重试/间隔/输出）**
   - 改 `scripts/batch_signup.py`

5. **适配 Auth0 页面结构变化**
   - 改 `tavily_register/core/register.py` 表单提取与提交路径

---

## 10. 质量保障建议

1. 先跑代理池测试：
   - `uv run python -m pytest tests/test_proxy_providers.py tests/test_properties.py tests/test_remaining.py -v`
2. 再做小规模端到端冒烟：
   - `uv run python scripts/batch_signup.py --count 1 --debug-init`
3. 每次改 `core/register.py` 后，优先验证：
   - 验证码识别
   - 登录态建立
   - `/api/keys` 获取与创建

---

## 11. 安全与合规

- `data/config.yaml` 可能包含 API 密钥，禁止入库。
- 输出文件可能包含敏感 key，避免共享。
- 仅用于合法测试用途，遵守目标平台条款与当地法律。

---

## 12. 维护约定

当出现以下变更时，必须同步更新本架构文档：

1. 新增/删除脚本入口（`scripts/`）
2. 核心流程步骤变化（注册、验证码、邮件验证、取 key）
3. 配置字段变化（`data/config.yaml`）
4. 目录结构调整（docs/scripts/data/package）

该文档应作为“重启上下文后的首读索引”。
