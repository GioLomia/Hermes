from pydantic import BaseModel


class AgentResult(BaseModel):
    def __init__(self) -> None:
        self.id: int
