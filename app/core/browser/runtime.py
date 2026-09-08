import json

from playwright.async_api import Page, CDPSession

from app.domain.browser_data import BrowserData


class Runtime:
    def __init__(self, page: Page, cdp: CDPSession, data: BrowserData):
        self.page: Page = page
        self.cdp: CDPSession = cdp
        self.data: BrowserData = data

        page.on("framenavigated", self._handle_navigated)

    async def _handle_navigated(self, frame):
        if frame.parent_frame is not None:
            return
        for hook in self.data.hook_registry:
            await self.page.evaluate(hook)

    async def add_hook(self, js_code: str):
        self.data.hook_registry.append(js_code)
        await self.page.evaluate(js_code)

    async def get_hook_data_by_id(self, hook_id: str):
        js_code = f"() => window.__agent_hooks__?.['{hook_id}'] || []"
        records = await self.page.evaluate(js_code)
        return records

    async def execute_js(self, js_code: str):
        wrapped = f"""
        (async () => {{
            try {{
                return await eval({json.dumps(js_code)});
            }} catch(e) {{
                return {{ __error: true, message: e.message, stack: e.stack }};
            }}
        }})()
        """

        resp = await self.cdp.send('Runtime.evaluate', {
            'expression': wrapped,
            'awaitPromise': True,
            'returnByValue': True,
            'userGesture': True,
        })

        return resp
