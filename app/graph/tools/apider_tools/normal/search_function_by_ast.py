import esprima

from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import BaseTool, ToolArgsDescription, ToolResult, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry
from app.util.ast_util import find_functions_by_keyword


@ToolRegistry.register
class SearchFunctionByAst(BaseTool):
    name = "search_function_by_ast"
    description = "使用ast，根据script_id在js文件中根据keyword进行搜索，返回function"
    args = [
        ToolArgsDescription(name="script_id", type=ToolArgsType.STR,description="js文件的script_id", required=True),
        ToolArgsDescription(name="keyword", type=ToolArgsType.STR,description="搜索关键词", required=True),
        ToolArgsDescription(name="max_chars", type=ToolArgsType.INT,description="最大字符数，默认1000", required=False)
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self, script_id:str,keyword:str,max_chars:int=1000)->ToolResult:
        try:
            code_with_line_list = await self.browser_oper.debug.get_script_code_by_id(script_id)
            js_code = ""
            for code_with_line in code_with_line_list:
                js_code += code_with_line["code"]
            functions_dict = await find_functions_by_keyword(js_code,keyword)
            result = [{
                "function_name": function["name"],
                "function_code": function["source"][:max_chars],
                "function_line":function["line"],
                "function_column":function["column"]
            } for function in functions_dict]

            if len(functions_dict)>0:
                return ToolResult.ok(result,f"在script_id:{script_id}中搜索到包含'{keyword}'的function共{len(functions_dict)}条")
            return ToolResult.error(f"在script_id:{script_id}中搜索{keyword}发生错误","未搜索到结果")
        except esprima.Error as e:
            return ToolResult.error(f"使用esprima解析js发生错误，script_id:{script_id},keyword:{keyword}",str(e))
        except Exception as e:
            return ToolResult.error(f"在script_id:{script_id}中搜索{keyword}发生未知错误",str(e))