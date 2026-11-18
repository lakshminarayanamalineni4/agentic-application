from app.config import LLM_API_KEY, LLM_MODEL
from app.schemas import ChatRequest
from openai import OpenAI


class BaseService:
    SYSTEM_PROMPT = (
        "You are a helpful AI assistant. "
        "Use available tools when they are useful. "
        "Answer clearly and concisely."
    )

    def __init__(self):
        self.model = LLM_MODEL
        self.client = OpenAI(
            api_key=LLM_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )