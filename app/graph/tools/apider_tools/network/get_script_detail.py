from dataclasses import asdict

from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import ToolResult, ToolArgsDescription, BaseTool, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class GetScriptDetail(BaseTool):
    name = "get_script_detail"
    description = "根据scriptId返回js详情"
    args = [
        ToolArgsDescription(name="script_id", type=ToolArgsType.STR,
                            description="要获取的js的script_id",required=True)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,script_id:str,start_line:int=1,
                  limit_line:int=10,max_line_len:int=500) -> ToolResult:
        """
        根据script_id获取js请求源信息
        """
        try:
            scripts_list = await self.browser_oper.debug.get_scripts_list()
            # 根据scriptid获取script_detail
            for script in scripts_list:
                if script.script_id == script_id:
                    return ToolResult.ok(data=[asdict(script)],
                                         summary=f"获取script_id:{script_id} js详情成功")
            return ToolResult.error(f"获取script_id:{script_id}详情失败",f"js详情为空")
        except Exception as e:
            return ToolResult.error( f"获取script_id:{script_id}详情失败", str(e))
