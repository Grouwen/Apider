import yaml

from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolResult, ToolArgsDescription, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry


@ToolRegistry.register
class GetAriaSnapshot(BaseTool):
    name = "get_aria_snapshot"
    description = "获取页面的可访问性树，用于操作网页，没有需要操作网页的需求不需要使用"
    args = [
        ToolArgsDescription("only_interaction",ToolArgsType.BOOL,
                            "是否只保留可交互的元素，默认True，强烈建议为True",False),
        ToolArgsDescription("yaml_schema", ToolArgsType.BOOL,
                            "是否使用yaml格式化输出，默认True，强烈建议为True，只有返回error格式化错误再改为False", False)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,only_interaction:bool=True,yaml_schema:bool=True) -> ToolResult:
        try:
            aria_snapshot = await self.browser_oper.dom.get_accessibility_tree(only_interaction)
            # 为空返回error
            if not aria_snapshot:
                return ToolResult.error("获取页面的可访问性树发生错误","可访问性树为空")

            # 是否yaml格式输出
            if not yaml_schema:
                return ToolResult.ok(data=[{"aria_snapshot":aria_snapshot}],summary="获取页面的可访问性树成功")

            # 使用yaml格式输出
            aria_snapshot = yaml.safe_load(aria_snapshot)
            return ToolResult.ok([aria_snapshot],"获取页面的可访问性树成功")
        except yaml.YAMLError as e:
            return ToolResult.error("使用yml解析失败", str(e))
        except Exception as e:
            return ToolResult.error("获取页面的可访问性树发生未知错误",str(e))