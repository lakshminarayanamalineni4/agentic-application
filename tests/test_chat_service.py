from types import SimpleNamespace

from app.schemas import ChatRequest
from app.services.chat import ChatService


def test_chat_service_builds_valid_messages():
    service = ChatService()

    messages = service.build_messages("explain rag")

    assert messages[0]["role"] == "system"
    assert isinstance(messages[0]["content"], str)
    assert messages[0]["content"] == "You are helpful AI assistant. Answer clearly and concisely."
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "explain rag"


def test_chat_request_is_extracted_to_string():
    service = ChatService()

    payload = ChatRequest(message="explain rag")

    assert service.extract_message(payload) == "explain rag"
    assert isinstance(service.extract_message(payload), str)


def test_chat_sends_string_message_content(monkeypatch):
    service = ChatService()
    captured = {}
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="A response"))]
    )

    def create_completion(**kwargs):
        captured.update(kwargs)
        captured["messages"] = [dict(message) for message in kwargs["messages"]]
        return response

    monkeypatch.setattr(
        service.client.chat.completions,
        "create",
        create_completion,
    )

    assert service.chat("explain rag") == "A response"
    assert captured["messages"] == [
        {
            "role": "system",
            "content": "You are helpful AI assistant. Answer clearly and concisely.",
        },
        {"role": "user", "content": "explain rag"},
    ]
