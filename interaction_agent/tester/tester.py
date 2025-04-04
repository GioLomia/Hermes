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

    def __init__(self, model: str):
        # Initialize the model
        self.llm = ChatGoogleGenerativeAI(
            model=model, api_key=SecretStr(os.getenv("GEMINI_API_KEY"))
        )

    def test(self, task: List[str], url: str):
        # Create agent with the model and URL
        agent = Agent(
            browser_context=b_context,
            task=f"{full_prompt}",
            llm=llm,
            controller=controller,
            initial_actions=initial_actions,
        )
