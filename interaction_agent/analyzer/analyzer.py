from pydantic import BaseModel
from typing import List
import json
import os


class Action(BaseModel):
    id: int
    action: str
    expected_outcome: str

class Actions(BaseModel):
    actions: List[Action]

class Analyzer:
    def __init__(self) -> None:
        self.output_structure = {}
        self.output = {}

    def cache_output(self, actions: Actions, output_path: str = "output"):
        """
        Store Actions object as a JSON file in the specified directory.
        
        Args:
            actions (Actions): The Actions object to store
            output_dir (str): Directory to store the JSON file (default: "output")
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_path, exist_ok=True)
            # Convert Actions to JSON
            parsed_actions = Actions.model_validate_json(actions)
            print(parsed_actions)
            # Write to file
            output_path = os.path.join(output_path, "actions.json")
            with open(output_path, "w") as f:
                f.write(parsed_actions.model_dump_json)
        except Exception as e:
            print(f"Error caching output: {e}")
            return None
        return output_path
