from typing import List
import argparse
import asyncio
import os

from browser_use import Agent, Browser, BrowserConfig, Controller
from browser_use.browser.context import BrowserContext, BrowserContextConfig
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import SecretStr

from interaction_agent.analyzer import Actions, Analyzer, Issues
from prompt_parser.prompt_parser import PromptParser


_default_browser_context_config = BrowserContextConfig(
    cookies_file="path/to/cookies.json",
    wait_for_network_idle_page_load_time=3.0,
    browser_window_size={"width": 1280, "height": 1100},
    locale="en-US",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    highlight_elements=True,
    viewport_expansion=500,
    allowed_domains=["saucedemo.com"],
)


class Tester:
    """
    A class that performs browser tests.
    """

    def __init__(
        self,
        model: str,
        context_prompt_path: str,
        browser_context_config: BrowserContextConfig = _default_browser_context_config,
    ):
        # Initialize the model
        self.llm = ChatGoogleGenerativeAI(
            model=model, api_key=SecretStr(os.getenv("GEMINI_API_KEY"))
        )
        self.prompt_context = PromptParser().parse_prompt(context_prompt_path)
        self.browser_context_config = browser_context_config
        self.browser_context = BrowserContext(
            browser=Browser(), config=self.browser_context_config
        )

    async def test(self, task: List[str], url: str):
        """
        Test the task on the url asynchronously.
        """
        results = []
        # Run tests concurrently or sequentially as needed
        # Example: Sequential execution
        for t in task:
            result = await self._run_test(t, url)
            results.append(result)
        # If concurrency is desired:
        # tasks_to_run = [self._run_test(t, url) for t in task]
        # results = await asyncio.gather(*tasks_to_run)

        return results

    async def _run_test(self, task: str, url: str):
        initial_actions = [{"open_tab": {"url": url}}]
        controller = Controller(output_model=Issues)
        # action_controller = Controller(output_model=Actions)
        agent = Agent(
            browser_context=self.browser_context,
            task=f"{self.prompt_context}\n{task}",
            llm=self.llm,
            controller=controller,
            initial_actions=initial_actions,
        )
        result = await agent.run(max_steps=15)
        return result
