import uuid
from typing import List

from app.common.constants import LOGPOINT_TAG
from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolResult, ToolArgsDescription, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class SetLogpoint(BaseTool):
    name = "set_logpoint"
    description = "设置日志断点，在console中打印变量"
    args = [
        ToolArgsDescription("url",ToolArgsType.STR,"js文件的url",True),
        ToolArgsDescription("line_number",ToolArgsType.INT,"设置logpoint的行数，从1开始",True),
        ToolArgsDescription("watch_variables", ToolArgsType.LIST, "要在断点中查看的变量名", True),
        ToolArgsDescription("column_number",ToolArgsType.INT,"设置logpoint的列数，从0开始，默认0",False),
        ToolArgsDescription("reload",ToolArgsType.BOOL,"设置断点后是否需要刷新。用于获得初始化数据，默认False",False),
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,url:str,
                  line_number:int,
                  watch_variables:List[str],
                  column_number:int=0,
                  reload:bool=False) -> ToolResult:
        try:
            # 处理变量，转为conlose中的语句
            log_message = ", ".join([
                f"'{v}', typeof {v} !== 'undefined' ? {v} : '[undefined]'"
                for v in watch_variables
            ])
            logpoint_uuid = str(uuid.uuid4())
            tagged_message = f"'{LOGPOINT_TAG}','{logpoint_uuid}', {log_message}"

            await self.browser_oper.debug.set_logpoint(logpoint_uuid,url,line_number-1,
                                                 column_number,tagged_message)
            if reload:
                await self.browser_oper.dom.reload()

            return ToolResult.ok( [{"logpoint_uuid":logpoint_uuid}], f"设置url:{url} 的logpoint成功。")
        except Exception as e:
            return ToolResult.error(f"设置url:{url} 的logpoint失败。",str(e))
