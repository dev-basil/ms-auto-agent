from dotenv import load_dotenv
import os
from langchain.chat_models import init_chat_model
from langchain_ollama import ChatOllama

load_dotenv()

use_ollama = os.getenv("USE_OLLAMA", "0") == "1"

if use_ollama:
    model = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0"))
    )
else:
    model = init_chat_model(os.getenv("GROQ_MODEL", "groq:openai/gpt-oss-120b"))