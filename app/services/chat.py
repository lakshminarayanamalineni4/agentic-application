from app.config import LLM_API_KEY, LLM_MODEL
from app.schemas import ChatRequest
from openai import OpenAI


class ChatService:
    SYSTEM_PROMPT = "You are helpful AI assistant. Answer clearly and concisely."

    def __init__(self):
        self.model = LLM_MODEL
        self.client = OpenAI(
            api_key=LLM_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )

        self.messages = [
            {
                "role": "system",
                "content": self.SYSTEM_PROMPT,
            }
        ]

    def build_messages(self, message: str) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

    @staticmethod
    def extract_message(payload: ChatRequest) -> str:
        return payload.message

    def chat(self, message: str) -> str:
        self.messages.append(self.build_messages(message)[1])

        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        assistant_message = response.choices[0].message.content

        self.messages.append(
            {
                "role": "assistant",
                "content": assistant_message
            }
        )

        return assistant_message