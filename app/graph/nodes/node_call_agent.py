from langchain_core.messages import AIMessage
from langgraph.runtime import Runtime
from app.graph.apider_context import ApiderContext
from app.graph.apider_state import ApiderState
from app.util.prompt_util import load_apider_user_message_prompt, load_prompt


async def node_call_agent(state:ApiderState,runtime:Runtime[ApiderContext]):
    user_input = state["user_input"]
    tools = state["tools"]
    short_memory_context_list = state.get("short_memory_context_list",[])
    history_compress = state.get("history_compress",{})
    llm_model = runtime.context["llm_model"]

    # 装载tool
    llm_model_with_tools = llm_model.bind_tools(tools)

    # 拼接message
    system_message = await load_prompt("apider_system_message.jinja2")
    user_message = await load_apider_user_message_prompt(user_input,history_compress)
    messages = [
        # {"role": "system", "content": "你是专业JS逆向工程师，根据用户需求，分析网站的接口使用了什么加密方式。"},
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    for result in short_memory_context_list:
        messages.append(result)

    # 调用llm
    resp:AIMessage = await llm_model_with_tools.ainvoke(messages)
    print("="*50+"\nllm回复：",resp.content)
    for i in resp.tool_calls:
        print("function：",i["name"],"\nargs:",i["args"])

    return {
        "llm_resp":resp
    }