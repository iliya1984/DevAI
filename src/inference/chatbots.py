from abc import ABC, abstractmethod
from src.data_access.reporting import ReportClient, IReportClient
from src.infra.configuration import ChatConfiguration
from ollama import Client
from pydantic import BaseModel
from src.rag.vector_store import IVectorStoreRetriever
import copy
import uuid
from datetime import datetime

class CompletionRequest(BaseModel):
    request_id: str = str(uuid.uuid4())
    messages: list = [dict[str, str]]


class CompletionStream:
    def __init__(self, stream):
        self.stream = stream
        self.vector_search_result = []

    def yield_chunks(self):
        for chunk in self.stream:
            # Extract text from the chunk
            chunk_text = chunk['message']['content']
            yield chunk_text

class IChatClient(ABC):
    @abstractmethod
    def completion_stream(self, request: CompletionRequest):
        pass

class OllamaChatClient(IChatClient):
    def __init__(
            self,
            vector_store_retriever: IVectorStoreRetriever,
            report_client: IReportClient,
            configuration: ChatConfiguration
    ):
        self.configuration = configuration
        self.vector_store_retriever =vector_store_retriever

        host = configuration.ollama.host
        self.client = Client(host=host)
        self.report_client = report_client

    def completion_stream(self, request: CompletionRequest):
        model = self.configuration.ollama.version
        messages = request.messages
        system_prompt = ("You are a coding assistant specialized in the LangGraph library. "
                         "Utilize the provided CONTEXT to answer the QUESTION. If the CONTEXT lacks sufficient information, "
                         "respond with I don't know based on the provided context.")

        message_history = [{ 'role': 'system', 'content': system_prompt }] + copy.deepcopy(messages)
        prompt = message_history[len(message_history) - 1]

        initial_user_prompt = prompt['content']
        prompt_content = 'QUESTION: ' + initial_user_prompt

        chunks_to_retrieve = self.configuration.completion.chunk_number
        vector_search_result = self.vector_store_retriever.query(query=prompt_content, k=chunks_to_retrieve)



        if len(vector_search_result) > 0:
            prompt_content += '\nCONTEXT: '
            for chunk in vector_search_result:
                prompt_content += '\n' + chunk.page_content

                record = {
                    "@timestamp": datetime.now().isoformat(),
                    "requestId": request.request_id,
                    "userPrompt" : initial_user_prompt,
                    "chunk" : chunk.page_content
                }
                self.report_client.report(record=record)

        prompt['content'] = prompt_content
        stream = self.client.chat(model=model, messages=message_history, stream=True)

        completion = CompletionStream(stream=stream)
        completion.vector_search_result = vector_search_result

        return completion