from operator import add
from typing import TypedDict, List, Dict, Any, Annotated

from langchain_core.messages import AIMessage


class ApiderState(TypedDict):
    user_input: str # 用户输入
    tools:List[dict] # 工具列表

    llm_resp:AIMessage # llm回复

    long_memory_context_list: Annotated[List[Dict[str, Any]], add] # 长期记忆（工具执行结果）
    short_memory_context_list: Annotated[List[Dict[str, Any]], add] # 短期记忆（工具执行结果）
    tool_count: int # 调用工具次数

    history_compress: Dict[str,Any] # 历史工具调用总结

    consume_tokens:int # 记录一次请求的消耗token数
    max_tool_count:int # 最大工具调用次数

    tool_token:int # 工具耗费token总数，达到MAX_COMPRESS_TOKEN_SIZE进行压缩