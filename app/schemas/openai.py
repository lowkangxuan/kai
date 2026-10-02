from typing import Literal
from pydantic import BaseModel, Field, model_validator


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class PromptRequest(BaseModel):
    messages: list[Message] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def validate_conversation(self):
        if sum(len(message.content) for message in self.messages) > 8000:
            raise ValueError("Conversation is too long.")

        if self.messages[-1].role != "user":
            raise ValueError("The last message must be from the user.")

        return self