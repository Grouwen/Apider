from dataclasses import asdict

from app.common.constants import MAX_SCRIPT_CODE_CHARS
from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import ToolResult, ToolArgsDescription, BaseTool, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class GetScriptCode(BaseTool):
    name = "get_script_code"
    description = "根据scriptId返回js源码"
    args = [
        ToolArgsDescription(name="script_id", type=ToolArgsType.STR,
                            description="要获取的js的script_id",required=True),
        ToolArgsDescription(name="start_line", type=ToolArgsType.INT,
                            description="从源码的第几行开始返回", required=True),
        ToolArgsDescription(name="start_column", type=ToolArgsType.INT,
                            description="从源码的第几列开始返回", required=True),
        ToolArgsDescription(name="end_line", type=ToolArgsType.INT,
                            description="获取源码结束行", required=True),
        ToolArgsDescription(name="end_column", type=ToolArgsType.INT,
                            description="获取源码结束列", required=True),
        ToolArgsDescription(name="max_len", type=ToolArgsType.INT,
                            description=f"返回的最大字符数，默认5000，不能超过{MAX_SCRIPT_CODE_CHARS}", required=False)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,script_id:str,start_line:int,start_column:int,
                  end_line:int,end_column:int,max_len:int=5000) -> ToolResult:
        """
        根据script_id获取js源码
        :param script_id: js的script_id
        :param start_line: 从源码的第几行开始返回
        :param start_column: 从源码的第几列开始返回
        :param end_line: 获取源码结束行
        :param end_column: 获取源码结束列
        :param max_len: 返回的最大字符数
        """
        try:
            if max_len > MAX_SCRIPT_CODE_CHARS:
                max_len = MAX_SCRIPT_CODE_CHARS
            code_with_line = await self.browser_oper.debug.get_script_code_by_id(script_id)
            # 截断code
            parts = []
            for item in code_with_line:
                line_no = item['line']
                code = item['code']

                # 跳过范围外的行
                if line_no < start_line or line_no > end_line:
                    continue

                # 确定当前行的切片范围
                col_start = start_column if line_no == start_line else 0
                col_end = end_column if line_no == end_line else len(code)

                parts.append(code[col_start:col_end])

            result = "\n".join(parts)
            result = result[:max_len]

            if result:
                return ToolResult.ok(data=[{"code": result}],
                                     summary=f"获取js源码成功。最大字符数:{max_len}")
            return ToolResult.error(f"获取script_id:{script_id}代码失败","js代码为空")
        except Exception as e:
            return ToolResult.error( f"获取script_id:{script_id}代码失败", str(e))