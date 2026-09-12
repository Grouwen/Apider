import json
from dataclasses import asdict
from typing import List, Dict, Any

from langchain_core.messages import ToolCall
from langgraph.runtime import Runtime

from app.graph.apider_context import ApiderContext
from app.graph.apider_state import ApiderState
from app.graph.tools.base import ToolResult

def _handle_tool_result_to_text(tool_results:List[Dict[str,ToolResult]])->List[Dict[str, Any]]:
    """
    将自定义tool_result转为function call格式
    规则：
    1.执行成功，data没值，content=summary
    2.执行成功，data有值，content=summary+data
    3.执行失败，content=summary+error_msg
    """
    final_results: List[Dict[str, Any]] = []
    for tool_result in tool_results:
        ((call_id, result),) = tool_result.items()
        result: ToolResult
        if result.success:
            if result.data:
                content = result.summary + "\n数据：" + "\n".join(json.dumps(item,ensure_ascii=False)
                                                                 for item in result.data)
            else:
                content = result.summary
        else:
            content = result.summary + "\n错误信息：" + result.error_msg
        final_results.append({
            "role": "tool",
            "tool_call_id": call_id,
            "content": content
        })
    return final_results

def _update_prompt(tool_name_str: str,
                           tool_args: Dict[str, Any],
                           result: ToolResult) -> Dict[str, List]:
    updates: Dict[str, List] = {}

    if tool_name_str == "add_facts":
        facts = tool_args.get("facts", [])
        if facts:
            updates["facts"] = facts
    elif tool_name_str == "list_scripts" and result.success and result.data:
        updates["script_list"] = result.data
    elif tool_name_str == "list_requests" and result.success and result.data:
        updates["request_list"] = result.data

    return updates

async def node_tool_run(state:ApiderState,runtime:Runtime[ApiderContext]):
    llm_resp = state["llm_resp"]
    request_list = state.get("request_list",[])
    script_list = state.get("script_list",[])
    facts = state.get("facts",[])
    tool_count = state.get("tool_count",0)
    tool_registry = runtime.context["tool_registry"]
    browser_oper = runtime.context["browser_oper"]


    update_prompt_dict: Dict[str, List] = {
        "facts": facts,
        "script_list": script_list,
        "request_list": request_list,
    }

    # 调用tool
    results:List[Dict[str,ToolResult]] = []
    for call in llm_resp.tool_calls:
        tool_name_str = call["name"].strip()
        tool_args = call["args"]
        try:
            call_cls = tool_registry.get(tool_name_str)
            tool = call_cls(browser_oper=browser_oper)
            result: ToolResult = await tool.run(**tool_args)
        except Exception as e:
            result = ToolResult.error(f"调用工具{call["name"]}出现错误", str(e))

        # 需要写回prompt
        updates = _update_prompt(tool_name_str, tool_args, result)
        for key, val in updates.items():
            update_prompt_dict[key].extend(val)

        results.append({call["id"]: result})
        tool_count += 1

    final_results:List[Dict[str, Any]] = []
    final_results.append({
        "role": "assistant",
        "content": llm_resp.content or "",
        "tool_calls": [tc if isinstance(tc, dict) else tc.model_dump()
                        for tc in llm_resp.tool_calls]
    })

    # 处理tool_reuslt变为functioncall格式
    for tool_result in results:
        ((call_id, result),) = tool_result.items()
        result: ToolResult
        final_results.append({
            "role": "tool",
            "tool_call_id": call_id,
            "content": asdict(result)
        })

    # 打印信息
    for i in final_results:
        if i["role"] == "tool":
            print(f"结果：{i["content"]}")
    print(f"调用工具次数：{tool_count}")

    # 返回
    return {
        "tool_count":tool_count,
        "long_memory_context_list": final_results,
        "short_memory_context_list": final_results,
        "current_tool_result":final_results,
        **update_prompt_dict,
    }
