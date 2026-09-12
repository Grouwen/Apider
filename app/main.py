import asyncio
import uuid

from langgraph.types import Command
from playwright.async_api import Playwright, Browser

from app.common.constants import USER_CONFIG_PATH
from app.config.user_config import UserConfig
from app.core.browser.browser_oper import BrowserOper
from app.graph.apider_context import ApiderContext
from app.graph.apider_graph import apider_app
from app.graph.apider_state import ApiderState
from app.graph.tools.tool_registry import ToolRegistry
from app.infrastructure.browser import init_playwright_and_browser
from app.infrastructure.compress_memory_llm_model import init_compress_memory_llm_model
from app.infrastructure.llm_model import init_llm_model

async def main(user_input:str,headless:bool = True):
    browser = None
    playwright = None

    try:
        # 初始化config
        user_config = UserConfig(USER_CONFIG_PATH)

        # 初始化 infrastructure
        llm_model = init_llm_model()
        compress_memory_llm_model = init_compress_memory_llm_model()
        playwright_and_browser = await init_playwright_and_browser(headless)
        playwright:Playwright = playwright_and_browser["playwright"]
        browser:Browser = playwright_and_browser["browser"]

        # 初始化 oper
        context = await browser.new_context()
        page = await context.new_page()
        cdp = await context.new_cdp_session(page)
        await cdp.send("Network.enable")
        await cdp.send("Debugger.enable")
        await cdp.send("Runtime.enable")
        browser_oper = BrowserOper(context, page, cdp)

        # 初始化tools
        tool_registry = ToolRegistry()
        tools = tool_registry.all_schemas()

        # 定义state
        apider_state = ApiderState(
            user_input=user_input,
            tools=tools,
        )
        apider_context = ApiderContext(
            llm_model=llm_model,
            compress_memory_llm_model=compress_memory_llm_model,
            browser_oper=browser_oper,
            tool_registry=tool_registry,
            user_config=user_config
        )

        # 运行graph
        thread_id = uuid.uuid4()
        config = {"configurable": {"thread_id": thread_id}}
        result = await apider_app.ainvoke(apider_state,context=apider_context,config=config)

        while "__interrupt__" in result:
            graph_message = result["__interrupt__"][0].value["message"]
            user_input = input(graph_message + "\n> ")  # 提示和收输入都得自己做
            result = await apider_app.ainvoke(Command(resume=user_input),
                                              context=apider_context,
                                              config=config)

    finally:
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()




if __name__ == '__main__':
    headless = False
    input_target = "分析这个页面数据加载逻辑https://spa2.scrape.center/"

    asyncio.run(main(input_target,headless))