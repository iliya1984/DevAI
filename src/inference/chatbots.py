from abc import ABC, abstractmethod
from src.infra.configuration import ChatConfiguration
from ollama import Client
from pydantic import BaseModel
from src.rag.vector_store import IVectorStoreRetriever
import copy

class CompletionRequest(BaseModel):
    messages: list = [dict[str, str]]


class IChatClient(ABC):
    @abstractmethod
    def completion_stream(self, request: CompletionRequest):
        pass

class OllamaChatClient(IChatClient):
    def __init__(
            self,
            vector_store_retriever: IVectorStoreRetriever,
            configuration: ChatConfiguration
    ):
        self.configuration = configuration
        self.vector_store_retriever =vector_store_retriever

        host = configuration.ollama.host
        self.client = Client(host=host)

    def completion_stream(self, request: CompletionRequest):
        model = self.configuration.ollama.version
        messages = request.messages
        system_prompt = ('You are a documentation assistant. Answer any question precisely. '
                         'If you do not know the answer. Say: I do not know the answer')

        message_history = [{ 'role': 'system', 'content': system_prompt }] + copy.deepcopy(messages)
        prompt = message_history[len(message_history) - 1]

        prompt_content = prompt['content']
        chunk_documents = self.vector_store_retriever.query(query=prompt_content, k=3)

        if len(chunk_documents) > 0:
            prompt_content += '\nAdditional Context:'
            for chunk in chunk_documents:
                prompt_content += '\n' + chunk.page_content

        prompt['content'] = prompt_content
        stream = self.client.chat(model=model, messages=message_history, stream=True)

        for chunk in stream:
            # Extract text from the chunk
            chunk_text = chunk['message']['content']
            yield chunk_text