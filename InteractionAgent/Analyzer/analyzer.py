from pydantic import BaseModel

class ActionAnalysis(BaseModel):
    id: int
    action: str
    expected_outcome: str

class Analyzer:
    def __init__(self) -> None:
        output_structure = {}
        output = {}