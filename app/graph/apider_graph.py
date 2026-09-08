from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from app.graph.apider_state import ApiderState
from app.graph.nodes.node_after_one_act import node_after_one_act
from app.graph.nodes.node_call_agent import node_call_agent
from app.graph.nodes.node_compress_memory import node_compress_memory
from app.graph.nodes.node_tool_run import node_tool_run


def route_after_llm(state: ApiderState) -> str:
    llm_resp = state.get("llm_resp")
    if llm_resp and getattr(llm_resp, "tool_calls", None):
        return "node_tool_run"
    return END

def route_after_one_act(state: ApiderState) -> str:
    max_tool_count = state["max_tool_count"]
    tool_count = state["tool_count"]
    if tool_count >= max_tool_count:
        return END
    return "node_call_agent"

graph = StateGraph(ApiderState)

graph.add_node("node_call_agent", node_call_agent)
graph.add_node("node_tool_run", node_tool_run)
graph.add_node("node_compress_memory", node_compress_memory)
graph.add_node("node_after_one_act", node_after_one_act)

graph.set_entry_point("node_call_agent")

graph.add_conditional_edges(
    "node_call_agent",
    route_after_llm,
    {
        "node_tool_run": "node_tool_run",
        END: END
    }
)

graph.add_edge("node_tool_run", "node_compress_memory")
graph.add_edge("node_compress_memory", "node_after_one_act")
graph.add_conditional_edges(
    "node_after_one_act",
    route_after_one_act,
    {
        "node_call_agent": "node_call_agent",
        END: END
    }
)

checkpointer = MemorySaver()
apider_app = graph.compile(checkpointer=checkpointer)