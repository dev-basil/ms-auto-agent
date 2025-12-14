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


def run_agent(task:str):
    input_message = {"role": "user", "content": f"""
                    Execute the the below task using the tools available.
                    Task: {task}
                    """}
    for step in agent_executor.stream(
        {"messages": [input_message]}, config, stream_mode="values"
    ):
        step["messages"][-1].pretty_print()