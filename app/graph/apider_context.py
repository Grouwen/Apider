from typing import TypedDict

from langchain_core.language_models import BaseChatModel

from app.config.user_config import UserConfig
from app.core.browser.browser_oper import BrowserOper
from app.graph.tools.tool_registry import ToolRegistry


class ApiderContext(TypedDict):
    llm_model:BaseChatModel
    compress_memory_llm_model:BaseChatModel
    tool_registry:ToolRegistry
    browser_oper:BrowserOper
    user_config:UserConfig