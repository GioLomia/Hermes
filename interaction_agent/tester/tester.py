from typing import List, Tuple
import argparse
import asyncio
import os

from browser_use import Agent, Browser, BrowserConfig, Controller
from browser_use.browser.context import BrowserContext, BrowserContextConfig
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from interaction_agent.result.agent_result import AgentResult
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
        max_steps: int = 5,
    ):
        # Initialize the model
        self.llm = ChatGoogleGenerativeAI(
            model=model, api_key=SecretStr(os.getenv("GEMINI_API_KEY"))
        )
        self.prompt_context = PromptParser().parse_prompt(context_prompt_path)
        self.browser_context_config = browser_context_config
        self.browsers: List[Browser] = []
        self.browser_contexts: List[BrowserContext] = []
        self.max_steps = max_steps

    async def test(self, task: List[str], url: str) -> List[AgentResult]:
        """
        Test the tasks on the url asynchronously and in parallel.
        """
        # Create coroutines for each task
        tasks_to_run = [self._run_test(t, url) for t in task]

        # Run tasks concurrently
        # Each result tuple contains (browser, browser_context, agent_result)
        results_with_resources: List[Tuple[Browser, BrowserContext, AgentResult]] = (
            await asyncio.gather(*tasks_to_run)
        )

        # Collect results and resources for cleanup
        final_results = []
        for browser, browser_context, agent_result in results_with_resources:
            if browser:
                self.browsers.append(browser)
            if browser_context:
                self.browser_contexts.append(browser_context)
            final_results.append(agent_result)

        return final_results

    async def _run_test(
        self, task: str, url: str
    ) -> Tuple[Browser | None, BrowserContext | None, AgentResult | None]:
        """
        Run a single test task in its own browser instance.
        Returns the browser, context, and result for cleanup and aggregation.
        """
        browser = None
        browser_context = None
        try:
            browser = Browser()
            browser_context = BrowserContext(
                browser=browser, config=self.browser_context_config
            )

            initial_actions = [{"open_tab": {"url": url}}]
            controller = Controller(output_model=Issues)
            agent = Agent(
                browser_context=browser_context,
                task=f"{self.prompt_context}\n{task}",
                llm=self.llm,
                controller=controller,
                initial_actions=initial_actions,
            )
            result = await agent.run(
                max_steps=self.max_steps
            )  # Consider adjusting max_steps if needed
            # Don't close browser/context here, return them for central cleanup
            return browser, browser_context, result
        except Exception as e:
            print(f"Error during test run for task '{task}': {e}")
            # Attempt partial cleanup if objects were created
            if browser_context:
                try:
                    await browser_context.close()
                except Exception as ce:
                    print(f"Error closing context during task error handling: {ce}")
            if browser:
                try:
                    await browser.close()
                except Exception as be:
                    print(f"Error closing browser during task error handling: {be}")
            return None, None, None  # Return None for resources and result on error

    async def close(self):
        """
        Close the browser context and the browser instance gracefully.
        """
        print("Attempting to close browser resources...")  # Added for debugging
        for browser, browser_context in zip(self.browsers, self.browser_contexts):
            try:
                if browser_context:
                    print("Closing browser context...")  # Added for debugging
                    await browser_context.close()
                    print("Browser context closed.")  # Added for debugging
            except Exception as e:
                print(f"Error closing browser context: {e}")

            try:
                if browser:
                    print("Closing browser...")  # Added for debugging
                    await browser.close()
                    print("Browser closed.")  # Added for debugging
                    browser = None  # Prevent potential double-closing
            except Exception as e:
                print(f"Error closing browser: {e}")

        # Add a small delay to allow background tasks to potentially clean up
        await asyncio.sleep(0.5)
        print("Finished closing browser resources.")  # Added for debugging
