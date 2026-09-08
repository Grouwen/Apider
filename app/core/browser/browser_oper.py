
from playwright.async_api import Browser, Page, BrowserContext, CDPSession

from app.core.browser.debug import Debug
from app.core.browser.dom import Dom
from app.core.browser.network import Network
from app.core.browser.runtime import Runtime
from app.domain.browser_data import BrowserData


class BrowserOper:
    def __init__(self,context:BrowserContext,
                 page:Page,cdp:CDPSession):
        self.context: BrowserContext = context
        self.page: Page = page
        self.cdp: CDPSession = cdp
        self.data = BrowserData()

        self.network = Network(self.cdp, self.data)
        self.debug = Debug(self.cdp, self.data)
        self.dom = Dom(self.page)
        self.runtime = Runtime(self.page,self.cdp,self.data)