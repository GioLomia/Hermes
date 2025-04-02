import os

import pytest

from .analyzer import Action, Actions, Analyzer


@pytest.fixture
def sample_actions():
    return Actions(
        actions=[
            Action(id=1, action="click", expected_outcome="button_clicked"),
            Action(id=2, action="type", expected_outcome="text_entered"),
        ]
    )


@pytest.fixture
def analyzer():
    return Analyzer()


def test_analyzer_initialization(analyzer):
    """Test if Analyzer initializes with empty dictionaries"""
    assert isinstance(analyzer.output_structure, dict)
    assert isinstance(analyzer.output, dict)
    assert len(analyzer.output_structure) == 0
    assert len(analyzer.output) == 0


def test_cache_output_default_path(analyzer, sample_actions, tmp_path):
    """Test caching output with default path"""
    # Use pytest's tmp_path fixture for temporary directory
    output_path = str(tmp_path)

    # Cache the output
    result_path = analyzer.cache_output(sample_actions, output_path)

    # Check if file was created
    assert os.path.exists(result_path)

    # Read and verify the content
    with open(result_path, "r") as f:
        content = f.read()
        assert '"id": 1' in content
        assert '"action": "click"' in content
        assert '"expected_outcome": "button_clicked"' in content


def test_cache_output_custom_path(analyzer, sample_actions, tmp_path):
    """Test caching output with custom path"""
    custom_path = str(tmp_path / "custom_dir")

    # Cache the output
    result_path = analyzer.cache_output(sample_actions, custom_path)

    # Check if file was created in custom directory
    assert os.path.exists(result_path)
    assert "custom_dir" in result_path


def test_cache_output_empty_actions(analyzer, tmp_path):
    """Test caching output with empty actions list"""
    empty_actions = Actions(actions=[])
    output_path = str(tmp_path)

    # Cache the output
    result_path = analyzer.cache_output(empty_actions, output_path)

    # Check if file was created
    assert os.path.exists(result_path)

    # Read and verify the content
    with open(result_path, "r") as f:
        content = f.read()
        assert '"actions": []' in content
