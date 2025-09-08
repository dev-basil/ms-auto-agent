from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from model import model
from agent_tools import tools

from typing import Any
memory = MemorySaver()

# worked deepseek-r1-distill-llama-70b
# groq:openai/gpt-oss-120b
# groq:llama-3.1-8b-instant
agent_executor = create_react_agent(model, tools, checkpointer=memory)
config: Any = {"configurable": {"thread_id": "abc123"}}


def run_agent(log:str):
    input_message = {"role": "user", "content": f"""Analyze the given log of the microservice and if there are any errors, perform the given actions to resolve them.
                    If the error is in fetching stock for book, restart "book-stock-service" service using the tool provided.
                    Do nothing if there are no errors. Avoid repeating the same action multiple times within 10 minutes.
                    Log: ${log}
                    """}
    for step in agent_executor.stream(
        {"messages": [input_message]}, config, stream_mode="values"
    ):
        step["messages"][-1].pretty_print()