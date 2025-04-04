import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import SecretStr

from interaction_agent.tester.tester import Tester, _default_browser_context_config


# Mock environment variable for API key
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_api_key")


@pytest.fixture
def mock_llm():
    """Fixture for a mocked LLM."""
    return MagicMock()


@pytest.fixture
def mock_prompt_parser():
    """Fixture for a mocked PromptParser."""
    mock = MagicMock()
    mock.parse_prompt.return_value = "Parsed context"
    return mock


@pytest.fixture
def mock_browser_context():
    """Fixture for a mocked BrowserContext."""
    mock = MagicMock()
    mock.close = AsyncMock()  # Mock the async close method if needed later
    return mock


@pytest.fixture
def mock_browser():
    """Fixture for a mocked Browser."""
    mock = MagicMock()
    mock.close = AsyncMock()
    return mock


@pytest.fixture
def mock_controller():
    """Fixture for a mocked Controller."""
    return MagicMock()


@pytest.fixture
def mock_agent():
    """Fixture for a mocked Agent."""
    mock = MagicMock()
    mock.run = AsyncMock(return_value="Agent run result")
    return mock


@pytest.fixture
@patch("interaction_agent.tester.tester.BrowserContext")
@patch("interaction_agent.tester.tester.Browser")
@patch("interaction_agent.tester.tester.PromptParser")
@patch("interaction_agent.tester.tester.ChatGoogleGenerativeAI")
def tester_instance(
    MockChatGoogleGenerativeAI,
    MockPromptParser,
    MockBrowser,
    MockBrowserContext,
    mock_llm,
    mock_prompt_parser,
    mock_browser,
    mock_browser_context,
):
    """Fixture to create a Tester instance with mocked dependencies."""
    MockChatGoogleGenerativeAI.return_value = mock_llm
    MockPromptParser.return_value = mock_prompt_parser
    MockBrowser.return_value = mock_browser
    MockBrowserContext.return_value = mock_browser_context

    # Ensure the API key environment variable is set if Tester relies on it directly
    # os.environ["GEMINI_API_KEY"] = "test_key" # Already handled by mock_env_vars

    tester = Tester(model="test-model", context_prompt_path="dummy_path.txt")
    # Allow re-assigning mocks if needed within tests, though ideally use the patch context
    tester.llm = mock_llm
    tester.prompt_context = mock_prompt_parser.parse_prompt.return_value
    tester.browser_context = mock_browser_context
    # Mock the internal browser instance if necessary, though BrowserContext mock might suffice
    # tester.browser_context.browser = mock_browser

    return tester


# --- Test Cases Will Go Here ---


@pytest.mark.asyncio
@patch("interaction_agent.tester.tester.Controller")
@patch("interaction_agent.tester.tester.Agent")
async def test_run_test_single_task(
    MockAgent,
    MockController,
    tester_instance,
    mock_agent,
    mock_controller,
):
    """Test the _run_test method."""
    MockController.return_value = mock_controller
    MockAgent.return_value = mock_agent

    task = "Test task description"
    url = "http://example.com"

    result = await tester_instance._run_test(task, url)

    # Verify Controller initialization
    MockController.assert_called_once()

    # Verify Agent initialization
    expected_initial_actions = [{"open_tab": {"url": url}}]
    expected_full_task = f"{tester_instance.prompt_context}\n{task}"
    MockAgent.assert_called_once_with(
        browser_context=tester_instance.browser_context,
        task=expected_full_task,
        llm=tester_instance.llm,
        controller=mock_controller,
        initial_actions=expected_initial_actions,
    )

    # Verify Agent.run call
    mock_agent.run.assert_awaited_once_with(max_steps=15)

    # Verify result
    assert result == "Agent run result"


@pytest.mark.asyncio
async def test_test_method_calls_run_test(tester_instance):
    """Test that the test method calls _run_test for each task."""
    tasks = ["task1", "task2"]
    url = "http://example.com"

    # Mock the internal _run_test method
    tester_instance._run_test = AsyncMock(side_effect=["result1", "result2"])

    results = await tester_instance.test(tasks, url)

    assert tester_instance._run_test.call_count == 2
    tester_instance._run_test.assert_any_await(tasks[0], url)
    tester_instance._run_test.assert_any_await(tasks[1], url)
    assert results == ["result1", "result2"]


def test_tester_initialization(
    tester_instance, mock_llm, mock_prompt_parser, mock_browser_context
):
    """Test the initialization of the Tester class."""
    assert tester_instance.llm == mock_llm
    assert tester_instance.prompt_context == "Parsed context"
    assert tester_instance.browser_context == mock_browser_context
    assert tester_instance.browser_context_config == _default_browser_context_config

    # Verify that the mocked classes were called during initialization
    # (This is implicitly tested by the tester_instance fixture setup)
    # For example, check if ChatGoogleGenerativeAI was called if needed
    # Or check if PromptParser's parse_prompt was called
    mock_prompt_parser.parse_prompt.assert_called_once_with("dummy_path.txt")
