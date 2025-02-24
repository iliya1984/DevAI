from abc import ABC, abstractmethod
from src.infra.configuration import ChatConfiguration
from ollama import Client
from pydantic import BaseModel

class CompletionRequest(BaseModel):
    messages: list = [dict[str, str]]


class IChatClient(ABC):
    @abstractmethod
    def completion_stream(self, request: CompletionRequest):
        pass

class OllamaChatClient(IChatClient):
    def __init__(self, configuration: ChatConfiguration):
        self.configuration = configuration

        host = configuration.ollama.host
        self.client = Client(host=host)

    def completion_stream(self, request: CompletionRequest):
        model = self.configuration.ollama.version
        stream = self.client.chat(model=model, messages=request.messages, stream=True)

        for chunk in stream:
            # Extract text from the chunk
            chunk_text = chunk['message']['content']
            yield chunk_text