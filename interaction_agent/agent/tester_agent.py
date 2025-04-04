import os

from browser_use import Agent, Browser, BrowserConfig, Controller
from browser_use.browser.context import BrowserContext, BrowserContextConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

_default_browser_config = BrowserConfig(headless=False, disable_security=False)

_default_browser_context_config = BrowserContextConfig(
    cookies_file="path/to/cookies.json",
    wait_for_network_idle_page_load_time=3.0,
    browser_window_size={"width": 1280, "height": 1100},
    locale="en-US",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    highlight_elements=True,
    viewport_expansion=500,
    allowed_domains=[],
)


class TesterAgent:
    def __init__(
        self,
        url: str,
        model: str,
        prompt_context_path: str,
        browser_config: BrowserConfig = _default_browser_config,
        browser_context_config: BrowserContextConfig = _default_browser_context_config,
        controller: Controller = None,
    ):
        self.url = url
        self.llm = ChatGoogleGenerativeAI(
            model=model, api_key=SecretStr(os.getenv("GEMINI_API_KEY"))
        )
        self.browser_config = browser_config
        self.browser_context_config = browser_context_config
        self.browser = Browser()
        self.browser_context = BrowserContext(
            browser=self.browser, config=self.browser_context_config
        )
        self.controller = controller
        self.agent = Agent(
            browser_context=self.browser_context,
            llm=self.llm,
            task="",
            controller=self.controller,
        )
        self.prompt_context = prompt_context_path

    def test(self, prompt: str, max_steps: int = 15):
        initial_actions = [{"open_tab": {"url": self.url}}]
