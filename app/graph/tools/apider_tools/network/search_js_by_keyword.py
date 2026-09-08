import re
import bisect
from typing import List

from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.base import ToolResult, ToolArgsDescription, BaseTool, ToolArgsType
from app.graph.tools.tool_registry import ToolRegistry

@ToolRegistry.register
class SearchJsByKeyword(BaseTool):
    name = "search_js_by_keyword"
    description = "在js中通过关键词进行搜索"
    args = [
        ToolArgsDescription("script_id_list",ToolArgsType.LIST,"要获取的js的script_id",True),
        ToolArgsDescription("keyword",ToolArgsType.STR,"要搜索的关键字",True),
        ToolArgsDescription("is_regex",ToolArgsType.BOOL,"是否开启正则",True),
        ToolArgsDescription("case_sensitive",ToolArgsType.BOOL,"是否区分大小写",True),
        ToolArgsDescription("max_matches",ToolArgsType.INT,"最多返回的匹配结果数量，默认10",False),
        ToolArgsDescription("context_chars",ToolArgsType.INT,"匹配点前后各截取的字符数，默认200",False),
    ]

    def __init__(self, browser_oper: BrowserOper):
        self.browser_oper = browser_oper

    async def run(self,script_id_list:List[str],keyword:str,
                       is_regex:bool,case_sensitive:bool,
                       max_matches:int=10,context_chars:int=200) -> ToolResult:

        results = []
        for scriptId in script_id_list:
            code_with_lines = await self.browser_oper.debug.get_script_code_by_id(scriptId)
            lines = [item["code"] for item in code_with_lines]
            js_code = "\n".join(lines)
            try:
                result = self._search_one(js_code, lines, keyword,is_regex,
                                      case_sensitive,max_matches,context_chars)
                results.append({
                    "script_id": scriptId,
                    "match": result
                })
            except re.error as e:
                results.append({
                    "script_id": scriptId,
                    "match": f"使用re匹配错误，错误原因:{str(e)}"
                })
        return ToolResult.ok(results,f"在script_id_list:{script_id_list.__str__()}中搜索关键字成功")

    def _search_one(self,js_code:str,lines:List[str],keyword:str,
                       is_regex:bool,case_sensitive:bool,
                       max_matches:int=10,context_chars:int=200):
        if is_regex:
            regex_flags = 0 if case_sensitive else re.IGNORECASE
            compiled = re.compile(keyword, regex_flags)
        else:
            escaped = re.escape(keyword)
            regex_flags = 0 if case_sensitive else re.IGNORECASE
            compiled = re.compile(escaped, regex_flags)

        # 预计算每行起始字符偏移，用于 char_offset → 行号转换
        line_offsets = []
        offset = 0
        for line in lines:
            line_offsets.append(offset)
            offset += len(line) + 1  # +1 是换行符

        def char_to_line_col(char_offset: int) -> tuple:
            """字符偏移 → (行号1-based, 列号0-based)"""
            idx = bisect.bisect_right(line_offsets, char_offset) - 1
            line_no = idx + 1
            col = char_offset - line_offsets[idx]
            return line_no, col

        all_matches = []
        for m in compiled.finditer(js_code):
            if len(all_matches) >= max_matches:
                break
            start_line, start_col = char_to_line_col(m.start())
            end_line, end_col = char_to_line_col(m.end())
            all_matches.append({
                "column_start": m.start(),
                "column_end": m.end(),
                "line_start": start_line,
                "line_end": end_line,
                "col_start": start_col,
                "col_end": end_col,
                "matched_text": m.group(),
            })

        # 2. 按上下文窗口合并：如果下一个匹配的起始位置 <= 上一个匹配的结束位置 + context_chars，
        #    说明它们落在同一个上下文窗口中，合并为一组
        groups: list[list[dict]] = []
        for match in all_matches:
            if not groups:
                groups.append([match])
            else:
                last_group = groups[-1]
                last_end_with_ctx = last_group[-1]["column_end"] + context_chars
                if match["column_start"] <= last_end_with_ctx:
                    last_group.append(match)
                else:
                    groups.append([match])

        # 3. 为每组生成一条结果
        results = []
        for group in groups:
            first = group[0]
            last = group[-1]
            ctx_start = max(0, first["column_start"] - context_chars)
            ctx_end = min(len(js_code), last["column_end"] + context_chars)
            prefix = "..." if ctx_start > 0 else ""
            suffix = "..." if ctx_end < len(js_code) else ""
            context = f"{prefix}{js_code[ctx_start:ctx_end]}{suffix}"

            matched_texts = [m["matched_text"] for m in group]

            unique_texts = list(dict.fromkeys(matched_texts))
            results.append({
                "line_start": first["line_start"],
                "line_end": last["line_end"],
                "column_start": first["col_start"],
                "column_end": last["col_end"],
                "matched_text": " | ".join(unique_texts),
                "context": context,
                "match_count": len(group),
            })

        return results