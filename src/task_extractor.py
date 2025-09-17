from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama


class ResponseFormatter(BaseModel):
    """Action needs to be done to resolve the error in the log"""

    action_needed: bool = Field(description="Whether action is needed or not")
    action: str = Field(description="Action to be taken to resolve the error")


model = ChatOllama(model="unsloth_model")


def task_extractor(log):
    model.with_structured_output(method="json_mode", schema=ResponseFormatter)
    ai_msg = str(model.invoke(log).content)
    print(ai_msg)
    if ai_msg.find("No error detected") == -1:
        return ai_msg
    return None


# task_extractor("Error: Error fetching stock for book")
