from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser
from pydantic import SecretStr
import os
from dotenv import load_dotenv
from browser_use import BrowserConfig
from browser_use.browser.context import BrowserContextConfig, BrowserContext
import asyncio

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))

    # Basic configuration
config = BrowserConfig(
    headless=False,
    disable_security=False
)


config = BrowserContextConfig(
    cookies_file="path/to/cookies.json",
    wait_for_network_idle_page_load_time=3.0,
    browser_window_size={'width': 1280, 'height': 1100},
    locale='en-US',
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36',
    highlight_elements=True,
    viewport_expansion=500,
    allowed_domains=[],
)

browser = Browser()
b_context = BrowserContext(browser=browser, config=config)


async def main():
    # Create agent with the model
    agent = Agent(
        browser_context=b_context,
        task="Open Youtube",
        llm=llm)
    result = await agent.run()
    print(result)

asyncio.run(main())