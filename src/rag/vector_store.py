import os
import re
import uuid

import requests
from langchain_chroma import Chroma
from langchain_core.documents import Document
from abc import ABC, abstractmethod
from langchain_huggingface import HuggingFaceEmbeddings
from src.infra.configuration import ChromaDBConfiguration, HuggingFaceEmbeddingConfiguration


class IVectorStoreRetriever(ABC):
    @abstractmethod
    def query(self, query: str, k: int = 5) -> list[dict]:
        pass

    @abstractmethod
    def embed(self, chunks):
        pass


class ChromaDbVectorStoreRetriever(IVectorStoreRetriever):
    def __init__(
            self,
            chroma_db_config: ChromaDBConfiguration,
            huggingface_embed_config: HuggingFaceEmbeddingConfiguration
    ):
        model_name = huggingface_embed_config.model_name
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': False}
        self.model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
            cache_folder=huggingface_embed_config.persist_directory
        )

        collection_name = chroma_db_config.collection_name
        persist_directory = chroma_db_config.persist_directory
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=self.model,
            persist_directory=persist_directory,  # Where to save data locally, remove if not necessary
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
