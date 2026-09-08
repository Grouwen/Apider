import asyncio

from playwright.async_api import Page


class Dom:
    def __init__(self,page:Page):
        self.page: Page = page

    async def goto(self,url:str,wait_for_load:int=5,timeout:int=1000*30):
        """
        打开新页面
        """
        await self.page.goto(url,timeout=timeout)
        await asyncio.sleep(wait_for_load)


    async def reload(self,wait_for_load:int=5,timeout:int=1000*30):
        """
        刷新页面
        """
        await self.page.reload(timeout=timeout)
        await asyncio.sleep(wait_for_load)

    async def get_accessibility_tree(self,only_interaction:bool=True):
        if only_interaction:
            return await self.page.aria_snapshot(mode="ai")
        return await self.page.aria_snapshot()

    async def click(self,ref:str):
        await self.page.locator(f"aria-ref={ref}").click()

    async def input(self,ref:str,input:str):
        await self.page.locator(f"aria-ref={ref}").fill(input)

    async def press(self,ref:str,name:str):
        await self.page.locator(f"aria-ref={ref}").press(name)

    async def scroll(self,x:int,y:int):
        await self.page.mouse.wheel(x, y)
