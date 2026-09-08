# Apider

> 基于 LLM Agent 的 JavaScript 逆向分析助手：让大模型像安全研究员一样，自主完成「抓包 → 定位加密代码 → 动态取证 → 算法还原」的完整逆向分析流程。

[![Python](https://img.shields.io/badge/python-%3E%3D3.12-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 项目简介

传统的 JS 逆向分析依赖人工在 DevTools 中反复打断点、翻调用栈、跟值，过程繁琐且高度依赖经验。Apider 将这一流程交给 LLM Agent 自主完成：

1. 通过 **Chrome DevTools Protocol (CDP)** 采集网络请求、脚本源码等静态证据；
2. 利用 **esprima AST 解析**在压缩混淆后的 JS 中精确定位目标函数；
3. 通过 **Logpoint（日志断点）与运行时 Hook** 获取闭包变量、函数输入输出等动态证据；
4. 基于「已观察 / 推测 / 已验证」三级证据分级，输出可回查、可复现的分析结论。

只需一句自然语言指令，例如：

```
分析这个页面数据加载逻辑 https://spa2.scrape.center/，不用在 python 中验证，只需要告诉我加密逻辑即可
```

Agent 会自主规划分析路径，调用工具收集证据，最终给出接口参数来源、构造过程、加密算法及编码顺序的完整说明。

## 核心特性

- **ReAct 式 Agent 架构**：基于 LangGraph 状态图实现 `LLM 决策 → 工具执行 → 证据回传 → 再决策` 的循环，支持 interrupt 人机交互
- **静态 + 动态结合的分析工具链**：封装 CDP Network / Debugger / Runtime 三大域，提供 15+ 个分析工具
- **AST 函数级定位**：基于 esprima 解析 JS 语法树，按关键词定位函数源码与行列号，避免全文读取大 bundle
- **长短记忆 + 上下文压缩**：工具结果按 token 阈值（默认 10k）触发 LLM 摘要压缩，支撑 30+ 轮长链路分析不爆上下文
- **证据分级 Prompt 工程**：System Prompt 强制区分「已观察 / 推测 / 已验证」，杜绝模型把猜测写成事实
- **噪声过滤**：内置请求噪声匹配规则（埋点上报、静态资源、第三方统计域名等），让 Agent 聚焦业务请求

## 系统架构

```
用户指令
   │
   ▼
┌─────────────────── LangGraph StateGraph ───────────────────┐
│                                                            │
│   ┌──────────────┐   有 tool_calls   ┌──────────────┐      │
│   │ node_call_   │ ────────────────▶ │ node_tool_   │      │
│   │ agent (LLM)  │                   │ run (工具执行)│      │
│   └──────▲───────┘                   └──────┬───────┘      │
│          │                                  │              │
│          │                          ┌───────▼───────┐      │
│          │                          │ node_compress_│      │
│          │                          │ memory(超阈值  │      │
│          │                          │ 则 LLM 压缩)   │      │
│          │                          └───────┬───────┘      │
│          │                          ┌───────▼───────┐      │
│          └───────────────────────── │ node_after_   │      │
│              未达最大工具次数        │ one_act(计数) │      │
│                                     └───────────────┘      │
└────────────────────────────────────────────────────────────┘
                            │
                            ▼
              ┌────── ToolRegistry（工具注册表）──────┐
              │  network │ debug │ dom │ runtime     │
              └──────────────────┬────────────────────┘
                                 ▼
              BrowserOper（CDP 封装：Network/Debugger/Runtime）
                                 ▼
                   Playwright + Chromium (CDP Session)
```

## 工具列表

| 分类 | 工具 | 说明 |
|---|---|---|
| network | `list_requests` | 列出捕获的网络请求（含噪声过滤） |
| network | `get_request_detail` | 查看请求详情（URL、请求头、调用栈） |
| network | `get_request_response` | 获取响应体 |
| network | `list_scripts` | 列出页面加载的 JS 脚本 |
| network | `get_script_detail` | 查看脚本元信息 |
| network | `get_script_code` | 按 script_id 读取脚本源码 |
| network | `search_js_by_keyword` | 在脚本中按关键词搜索 |
| normal | `search_function_by_ast` | 基于 esprima AST 按关键词定位函数（名称、源码、行列号） |
| debug | `set_logpoint` | 在指定源码位置设置日志断点 |
| debug | `get_logpoint_data` | 读取日志断点捕获的数据 |
| runtime | `add_hook` | 对页面全局函数/对象方法注入 Hook |
| runtime | `get_hook_data` | 读取 Hook 捕获的输入输出 |
| runtime | `execute_js` | 在页面上下文执行 JS（用于只读查询与计算验证） |
| dom | `open_url` / `click_dom` / `input_dom` / `scroll` / `get_aria_snapshot` | 浏览器交互，用于触发目标行为 |

## 快速开始

### 环境要求

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)（推荐）或 pip

### 安装

```bash
git clone <your-repo-url>
cd apider

# 安装依赖
uv sync

# 安装浏览器
uv run playwright install chromium
```

### 配置

复制环境变量模板并填入模型配置（支持任意 OpenAI 兼容接口）：

```bash
cp .env-example .env
```

```ini
# .env
# 主分析模型（建议使用工具调用能力强的模型）
MODEL_LLM_MODEL=gpt-4o
MODEL_LLM_API_KEY=sk-xxxx
MODEL_LLM_BASE_URL=https://api.openai.com/v1

# 记忆压缩模型（可使用更便宜的模型）
COMPRESS_MEMORY_MODEL_LLM_MODEL=gpt-4o-mini
COMPRESS_MEMORY_MODEL_LLM_API_KEY=sk-xxxx
COMPRESS_MEMORY_MODEL_LLM_BASE_URL=https://api.openai.com/v1
```

### 运行

修改 `app/main.py` 中的分析目标，然后：

```bash
uv run python -m app.main
```

## 项目结构

```
├── app/
│   ├── main.py                    # 入口：初始化 LLM / 浏览器 / 工具，运行 graph
│   ├── common/constants.py        # 常量：压缩阈值、噪声过滤规则等
│   ├── config/                    # 模型配置（pydantic-settings）
│   ├── core/browser/              # CDP 封装层：network / debug / dom / runtime
│   ├── domain/                    # 数据模型：请求、响应、脚本、断点数据
│   ├── graph/                     # LangGraph 状态图
│   │   ├── apider_graph.py        # 图定义与路由
│   │   ├── apider_state.py        # 状态定义（长短记忆、token 计数）
│   │   ├── nodes/                 # 节点：LLM 调用 / 工具执行 / 记忆压缩 / 计数
│   │   └── tools/                 # 工具注册表与 15+ 分析工具
│   ├── infrastructure/            # 浏览器与 LLM 初始化
│   └── util/                      # AST、提示词、token 计数等工具函数
├── prompts/                       # Jinja2 提示词模板
│   ├── apider_system_message.jinja2   # 系统提示词（分析方法论 + 证据分级）
│   ├── apider_user_message.jinja2
│   └── compress_memory.jinja2         # 记忆压缩提示词
├── pyproject.toml
└── uv.lock
```

## 关键设计

### 长短记忆与上下文压缩

逆向分析往往需要 20~30 轮工具调用，原始工具结果（网络报文、JS 源码）体积巨大。Apider 将工具结果分为：

- **短期记忆**：最近一次压缩后的完整工具结果，直接注入上下文
- **长期记忆**：历史压缩摘要（`history_compress`），记录已确认的接口、参数与进度

当短期记忆累计 token 超过 `MAX_COMPRESS_TOKEN_SIZE`（默认 10k）时，由独立的压缩模型将其摘要为结构化 JSON，既控制成本又保留可回查的证据链。

### 证据分级

System Prompt 强制模型区分三类信息，防止「幻觉式逆向」：

| 级别 | 含义 |
|---|---|
| 已观察 | 工具实际返回的请求、源码、变量或调用记录 |
| 推测 | 根据现象提出、尚未充分确认的解释 |
| 已验证 | 具有明确验证过程和结果的结论 |

## 免责声明

本项目仅用于**安全研究与学习目的**，演示目标均为公开的爬虫练习站点。请勿将其用于对未经授权的网站进行数据抓取、绕过访问控制或其他违反目标网站服务条款与相关法律法规的行为。使用者需自行承担使用本工具产生的一切法律责任。

## License

[MIT](LICENSE)
