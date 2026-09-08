from typing import Dict, Any

from playwright.async_api import async_playwright, Browser, Playwright


async def init_playwright_and_browser(headless:bool=True)->Dict[str,Any]:
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    return {
        "playwright":playwright,
        "browser": browser,
    }

async def stop_playwright_and_browser(playwright:Playwright,browser:Browser):
    await playwright.stop()
    await browser.close()