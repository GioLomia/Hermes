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

load_dotenv()

from lmnr import Laminar

# this line auto-instruments Browser Use and any browser you use (local or remote)
Laminar.initialize(os.getenv("LMNR_PROJECT_API_KEY"))

api_key = os.getenv("GEMINI_API_KEY")

# Initialize the model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro-exp-03-25", api_key=SecretStr(os.getenv("GEMINI_API_KEY"))
)

# Basic configuration
config = BrowserConfig(headless=False, disable_security=False)

config = BrowserContextConfig(
    cookies_file="path/to/cookies.json",
    wait_for_network_idle_page_load_time=3.0,
    browser_window_size={"width": 1280, "height": 1100},
    locale="en-US",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36",
    highlight_elements=True,
    viewport_expansion=500,
    allowed_domains=["saucedemo.com"],
)

browser = Browser()
b_context = BrowserContext(browser=browser, config=config)
controller = Controller(output_model=Issues)
action_controller = Controller(output_model=Actions)


async def main(url=None):
    prompt_parser = PromptParser()
    context = prompt_parser.parse_prompt("Prompts/Analysis/context.txt")
    prompt = "Buy 10 backpack"
    full_prompt = f"{context}\n{prompt}"
    if url:
        initial_actions = [{"open_tab": {"url": url}}]
        # config.allowed_domains.append(url)

        print(initial_actions)
        print(config)

        # Create agent with the model and URL
        agent = Agent(
            browser_context=b_context,
            task=f"{full_prompt}",
            llm=llm,
            controller=controller,
            initial_actions=initial_actions,
        )
        result = await agent.run(max_steps=15)

        print(result.final_result)
        print(result.model_actions)
        print(result.errors)
        # Ensure proper cleanup order
        await b_context.close()  # Then close browser context
        await browser.close()  # Finally close browser

    else:
        print(full_prompt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the browser automation with optional URL input"
    )
    parser.add_argument("--url", type=str, help="URL to analyze")
    args = parser.parse_args()

    asyncio.run(main(args.url))
