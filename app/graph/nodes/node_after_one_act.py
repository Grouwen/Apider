from app.common.constants import MAX_TOOL_COUNT
from app.graph.apider_state import ApiderState
from app.util.graph_util import hitl_is_continue


async def node_after_one_act(state:ApiderState):
    llm_resp = state["llm_resp"]
    tool_count = state["tool_count"]
    max_tool_count = state.get("max_tool_count", MAX_TOOL_COUNT)
    consume_tokens = state.get("consume_tokens",0)

    # 写回

    # 计算token
    total_tokens = llm_resp.usage_metadata.get("total_tokens", 0) if llm_resp.usage_metadata else 0
    input_tokens = llm_resp.usage_metadata.get("input_tokens", 0) if llm_resp.usage_metadata else 0
    consume_tokens += int(total_tokens)

    # 限制工具调用次数
    if tool_count >= max_tool_count:
        is_continue = hitl_is_continue(f"工具调用达到最大次数（{state["tool_count"]}/{max_tool_count}），是否增加10次工具调用")
        if is_continue:
            max_tool_count = tool_count+10


    print(f"本轮input_tokens:{input_tokens}")
    print(f"截至目前共消耗token:{consume_tokens}")

    return {
        "max_tool_count":max_tool_count,
        "consume_tokens":consume_tokens
    }