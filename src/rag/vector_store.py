import os
import re
import uuid

import requests
import numpy as np
import openai
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

model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings_model = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
    cache_folder=f'{os.getcwd()}/models'
)

vector_store = Chroma(
    collection_name="travel_company_policies",
    embedding_function=embeddings_model,
    persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
)

class IVectorStoreRetriever(ABC):
    @abstractmethod
    def query(self, query: str, k: int = 5) -> list[dict]:
        pass


class ChromaDbVectorStoreRetriever(IVectorStoreRetriever):
    def __init__(self, model):
        self.model = model

    @classmethod
    def from_docs(cls, docs):

        id = 0
        documents = []
        for d in docs:
            id += 1
            document = Document(
                page_content=d["page_content"],
                id=id
            )
            documents.append(document)

        uuids = [str(uuid.uuid4()) for _ in range(len(documents))]
        vector_store.add_documents(documents=documents, ids=uuids)



    def query(self, query: str, k: int = 5) -> list[dict]:
        pass

class VectorStoreRetriever(IVectorStoreRetriever):
    def __init__(self, docs: list, vectors: list, oai_client):
        self._arr = np.array(vectors)
        self._docs = docs
        self._client = oai_client

    @classmethod
    def from_docs(cls, docs, oai_client):
        embeddings = oai_client.embeddings.create(
            model="text-embedding-3-small", input=[doc["page_content"] for doc in docs]
        )
        vectors = [emb.embedding for emb in embeddings.data]
        return cls(docs, vectors, oai_client)

    def query(self, query: str, k: int = 5) -> list[dict]:
        embed = self._client.embeddings.create(
            model="text-embedding-3-small", input=[query]
        )
        # "@" is just a matrix multiplication in python
        scores = np.array(embed.data[0].embedding) @ self._arr.T
        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        return [
            {**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted
        ]


#retriever = VectorStoreRetriever.from_docs(docs, openai.Client())