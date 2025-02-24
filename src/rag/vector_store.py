import os
import re
import uuid

import requests
from langchain_chroma import Chroma
from langchain_core.documents import Document
from abc import ABC, abstractmethod

response = requests.get(
    "https://storage.googleapis.com/benchmarks-artifacts/travel-db/swiss_faq.md"
)
response.raise_for_status()
faq_text = response.text

docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]

from langchain_huggingface import HuggingFaceEmbeddings



class IVectorStoreRetriever(ABC):
    @abstractmethod
    def query(self, query: str, k: int = 5) -> list[dict]:
        pass

    @abstractmethod
    def embed(self, chunks):
        pass


class ChromaDbVectorStoreRetriever(IVectorStoreRetriever):
    def __init__(self):
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        self.model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
            cache_folder=f'{os.getcwd()}/models'
        )

        self.vector_store = Chroma(
            collection_name="travel_company_policies",
            embedding_function=self.model,
            persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
        )

    def embed(self, chunks):

        id = 0
        documents = []
        for chunk in chunks:
            id += 1
            document = Document(
                page_content=chunk,
                id=id
            )
            documents.append(document)

        uuids = [str(uuid.uuid4()) for _ in range(len(documents))]
        self.vector_store.add_documents(documents=documents, ids=uuids)



    def query(self, query: str, k: int = 5) -> list[Document]:
        return self.vector_store.similarity_search(query=query, k=k)
