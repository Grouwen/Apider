from pathlib import Path
from typing import Final

# 提示词文件路径
PROMPT_FILE_PATH: Final[Path] = Path(__file__).parents[2] / "prompts"

# logpoint标识
LOGPOINT_TAG = "[CHAR_LOGPOINT]"

# 最大触发总结的token数
MAX_COMPRESS_TOKEN_SIZE = 4*10000

# get_script_code最大字符数
MAX_SCRIPT_CODE_CHARS = 20000

# 噪声匹配
GENERIC_NOISE_PATTERNS = (
    # 1) 浏览器内部协议与动态内存协议 (过滤 data:image, blob 等，但保留 data:application/wasm 供后续解析)
    r'^(blob|about|javascript|view-source|chrome|devtools):',
    r'^data:(?!application/(wasm|json))',  # 负向预查：过滤 data:image, data:text 等，放行 wasm 和 json

    # 2) 动态脚本占位符 (eval / new Function 产生的匿名脚本)
    r'^VM\d+$',

    # 3) 静态资源后缀 (⚠️ 移除了 map，避免误杀 SourceMap 解析事件)
    r'\.(m4s|m3u8|mp4|webm|flv|ts|mov|avi|mkv'
    r'|mp3|m4a|aac|ogg|wav|flac|opus'
    r'|jpg|jpeg|png|gif|webp|avif|bmp|ico|svg'
    r'|woff2?|ttf|otf|eot'
    r'|zip|gz|tgz|rar|7z|tar'
    r'|wasm|exe|dmg|apk|cnf|conf)([?#]|$)',

    # 4) 通用埋点/上报端点命名
    r'/(collect|beacon|telemetry|metrics|heartbeat|tracks?|events?|logs?|batch|ping)([/?#]|$)',

    # 5) 第三方统计/监控域名
    r'^https?://[^/]*(google-analytics\.com|googletagmanager\.com|doubleclick\.net'
    r'|analytics\.google\.com|sentry\.(io|com)|bugsnag\.(io|com)|hotjar\.com'
    r'|clarity\.ms|mixpanel\.com|amplitude\.com|segment\.(io|com)|nr-data\.net'
    r'|datadoghq\.(com|eu)|fullstory\.com|logrocket\.(com|io)'
    r'|umeng\.com|cnzz\.com|51\.la|appsflyer\.com|adjust\.com|branch\.io'
    r'|sensorsdata\.cn|growingio\.com|hm\.baidu\.com|hmma\.baidu\.com'
    r'|matomo\.(io|cloud)|plausible\.io|posthog\.com)',

    # 6) 裸 IP 主机
    r'^https?://\d{1,3}(\.\d{1,3}){3}(:\d+)?/',
)

# 最大工具调用次数
MAX_TOOL_COUNT = 30