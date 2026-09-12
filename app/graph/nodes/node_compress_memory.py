from langchain_core.output_parsers import JsonOutputParser
from langgraph.runtime import Runtime
from langgraph.types import Overwrite

from app.common.constants import MAX_COMPRESS_TOKEN_SIZE
from app.graph.apider_context import ApiderContext
from app.graph.apider_state import ApiderState
from app.util.prompt_util import load_compress_memory_prompt
from app.util.token_count_util import count_message_tokens


async def node_compress_memory(state: ApiderState, runtime: Runtime[ApiderContext]):
    user_input = state["user_input"]
    tool_token = state.get("tool_token", 0)  # 工具耗费token总数，达到max_compresss_token_size进行压缩
    short_memory_context_list = state["short_memory_context_list"]  # 短期tool调用历史
    current_tool_result = state["current_tool_result"] # 当前turn的记录
    history_compress = state.get("history_compress", {})  # 历史压缩记录
    compress_memory_llm_model = runtime.context["compress_memory_llm_model"]
    user_config = runtime.context["user_config"]
    # 获取最大触发总结的token数，没有就使用默认值
    max_compresss_token_size = user_config.get("graph.compress.token_size",MAX_COMPRESS_TOKEN_SIZE)

    # 粗略计算是否达到max_compresss_token_size
    this_token = count_message_tokens(short_memory_context_list)
    # 计入tool_token
    tool_token += this_token
    print(f"本次tool耗费token{this_token}")
    print(f"距离上次压缩tool总共耗费token{tool_token}")
    if not tool_token > max_compresss_token_size:
        return {
            "history_compress": history_compress,
            "tool_token": tool_token
        }

    # 加载提示词，调用llm进行总结
    print(f"tool_result达到{max_compresss_token_size}，触发压缩")
    chain = compress_memory_llm_model | JsonOutputParser()
    no_current_tool_result = [item for item in short_memory_context_list if item not in current_tool_result]
    try:
        compress_memory_prompt = await load_compress_memory_prompt(user_input,
                                                                   history_compress,
                                                                   no_current_tool_result)
        history_compress = await chain.ainvoke(compress_memory_prompt)

    except Exception as e:
        print("调用压缩llm失败，错误原因：",str(e))
        return {
            "history_compress": history_compress,
            "tool_token": tool_token
        }

    print(f"压缩后的数据:{history_compress}")

    return {
        "history_compress": history_compress,
        "short_memory_context_list": Overwrite([]),
        "tool_token": 0
    }
