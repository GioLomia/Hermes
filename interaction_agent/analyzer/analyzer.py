import json
import os
from typing import List

from pydantic import BaseModel
from interaction_agent.result.agent_result import AgentResult


class Action(BaseModel):
    def __init__(self) -> None:
        self.description: str
        self.steps: List[str]


class Actions(AgentResult):
    def __init__(self) -> None:
        self.actions: List[Action]


class Issue(BaseModel):
    def __init__(self) -> None:
        self.success: bool
        self.description: str
        self.steps_to_reproduce: str
        self.expected_outcome: str
        self.actual_outcome: str


class Issues(AgentResult):
    def __init__(self) -> None:
        self.actions: List[Issue]


class Analyzer:
    def __init__(self) -> None:
        self.output_structure = {}
        self.output = {}

    def cache_output(self, issues: Issues, output_path: str = "output"):
        """
        Store Issues object as a JSON file in the specified directory.

        Args:
            issues (Issues): The Issues object to store
            output_dir (str): Directory to store the JSON file (default: "output")
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_path, exist_ok=True)
            # Convert Issues to JSON
            parsed_issues = Issues.model_validate_json(issues)
            print(parsed_issues)
            # Write to file
            output_path = os.path.join(output_path, "issues.json")
            with open(output_path, "w") as f:
                f.write(parsed_issues.model_dump_json())
        except Exception as e:
            print(f"Error caching output: {e}")
            return None
        return output_path
