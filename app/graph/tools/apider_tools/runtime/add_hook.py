import uuid

from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolArgsDescription, ToolArgsType, ToolResult
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class AddHook(BaseTool):
    name = "add_hook"
    description = "在页面中注入 JS Hook，拦截指定全局函数的调用并记录参数、返回值、调用栈"
    args = [
        ToolArgsDescription("function_path", ToolArgsType.STR, "函数路径，如 window.fetch、CryptoJS.MD5、localStorage.setItem", required=True),
        ToolArgsDescription("capture_args", ToolArgsType.BOOL, "是否记录参数，默认 true", required=False),
        ToolArgsDescription("capture_return", ToolArgsType.BOOL, "是否记录返回值，默认 true", required=False),
        ToolArgsDescription("capture_stack", ToolArgsType.BOOL, "是否记录调用栈，默认 true", required=False),
        ToolArgsDescription("max_records", ToolArgsType.INT, "最多记录条数，默认 50", required=False),
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self, function_path: str, capture_args=True, capture_return=True, capture_stack=True,
                  max_records=50) -> ToolResult:
        hook_id = uuid.uuid4().hex[:8]

        js = f"""
        () => {{
            window.__agent_hooks__ = window.__agent_hooks__ || {{}};
            window.__agent_hooks__['{hook_id}'] = [];

            var path = '{function_path}';
            var parts = path.split('.');
            var method = parts.pop();

            // ========== 核心修复：延迟 Hook ==========
            function doHook() {{
                var obj = window;
                for (var i = 0; i < parts.length; i++) {{
                    obj = obj[parts[i]];
                    if (!obj) return false;  // 路径不存在，返回 false 等待重试
                }}

                var orig = obj[method];
                if (!orig) return false;  // 函数不存在，返回 false 等待重试

                // 避免重复 Hook
                if (orig.__hooked_by_{hook_id}) return true;

                obj[method] = function() {{
                    var rec = {{ timestamp: new Date().toISOString() }};

                    if ({str(capture_args).lower()}) {{
                        rec.args = Array.from(arguments).map(a => {{
                            try {{ return JSON.stringify(a).substring(0, 500); }} catch(e) {{ return String(a).substring(0, 500); }}
                        }});
                    }}

                    if ({str(capture_stack).lower()}) {{
                        rec.stack = new Error().stack;
                    }}

                    var result;
                    try {{
                        result = orig.apply(this, arguments);
                    }} catch(err) {{
                        rec.type = 'error';
                        rec.error = String(err.message || err).substring(0, 500);
                        window.__agent_hooks__['{hook_id}'].push(rec);
                        if (window.__agent_hooks__['{hook_id}'].length > {max_records}) {{
                            window.__agent_hooks__['{hook_id}'].shift();
                        }}
                        throw err;
                    }}

                    if ({str(capture_return).lower()}) {{
                        if (result && typeof result.then === 'function') {{
                            result.then(
                                val => {{
                                    window.__agent_hooks__['{hook_id}'].push({{
                                        timestamp: new Date().toISOString(),
                                        type: 'return',
                                        returnValue: (function(){{ try{{ return JSON.stringify(val).substring(0,500); }}catch(e){{ return String(val).substring(0,500); }} }})()
                                    }});
                                }},
                                err => {{
                                    window.__agent_hooks__['{hook_id}'].push({{
                                        timestamp: new Date().toISOString(),
                                        type: 'return',
                                        returnValue: 'Promise rejected: ' + String(err).substring(0, 500)
                                    }});
                                }}
                            );
                        }} else {{
                            try {{ rec.returnValue = JSON.stringify(result).substring(0, 500); }} catch(e) {{ rec.returnValue = String(result).substring(0, 500); }}
                        }}
                    }}

                    rec.type = rec.type || 'call';
                    window.__agent_hooks__['{hook_id}'].push(rec);
                    if (window.__agent_hooks__['{hook_id}'].length > {max_records}) {{
                        window.__agent_hooks__['{hook_id}'].shift();
                    }}

                    return result;
                }};

                obj[method].__hooked_by_{hook_id} = true;
                return true;
            }}

            // 立即尝试 Hook
            if (doHook()) {{
                return {{ success: true, hook_id: '{hook_id}', delayed: false }};
            }}

            // ========== 延迟 Hook：轮询等待目标加载 ==========
            var attempts = 0;
            var maxAttempts = 100;  // 最多 10 秒（100 * 100ms）

            var interval = setInterval(function() {{
                attempts++;
                if (doHook()) {{
                    clearInterval(interval);
                    console.log('[Hook] 延迟 Hook 成功: {function_path}');
                }} else if (attempts >= maxAttempts) {{
                    clearInterval(interval);
                    console.error('[Hook] 延迟 Hook 超时: {function_path}');
                }}
            }}, 100);

            return {{ success: true, hook_id: '{hook_id}', delayed: true, message: '目标尚未加载，已启动延迟 Hook（最多等待10秒）' }};
        }}
        """

        try:
            await self.browser_oper.runtime.add_hook(js)
            return ToolResult.ok(data=[{"hook_id": hook_id}],summary=f"成功注入Hook: {function_path} hook_uuid: {hook_id}")
        except Exception as e:
            return ToolResult.error(f"注入hook:{function_path}失败",str(e))