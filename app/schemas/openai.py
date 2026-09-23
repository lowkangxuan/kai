from typing import Literal
from pydantic import BaseModel, Field

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)

class PromptRequest(BaseModel):
    messages: list[Message]