from pydantic import BaseModel, Field
from model import model


class ResponseFormatter(BaseModel):
    """Action needs to be done to resolve the error in the log"""

    action_needed: bool = Field(description="Whether action is needed or not")
    action: str = Field(description="Action to be taken to resolve the error")


def task_extractor(log):
    model.with_structured_output(method="json_mode", schema=ResponseFormatter)
    ai_msg = str(model.invoke(log).content)
    print(ai_msg)
    if ai_msg.find("No error detected") == -1:
        return ai_msg
    return None
