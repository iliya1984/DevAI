from pydantic import BaseModel
from abc import ABC, abstractmethod
from src.infra.configuration import EmbeddingConfiguration
from src.data_access.graphs import DocumentGraph
from src.rag.vector_store import IVectorStoreRetriever
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter

class EmbeddingRequest(BaseModel):
    document_id: str

class IEmbedder(ABC):
    @abstractmethod
    def embed(self, request: EmbeddingRequest):
        pass

class DocumentEmbedder(IEmbedder):
    def __init__(
            self,
            graph: DocumentGraph,
            vector_store_retriever: IVectorStoreRetriever,
            configuration: EmbeddingConfiguration
    ):
        self.graph = graph
        self.configuration = configuration
        self.vector_store_retriever = vector_store_retriever

    def embed(self, request: EmbeddingRequest):
        document_id = request.document_id
        document_node = self.graph.get_document_node_by_id(document_id=document_id)

        if document_node is None:
            raise Exception(f'Unable to create a document embeddings with id={document_id}. Document was not found')

        parsed_file_path = document_node.parsing_storage_path

        if parsed_file_path is None:
            raise Exception(f'Unable to create a document embeddings with id={document_id}. '
                            'Parsed document path was not found')

        file_exists = Path(parsed_file_path).exists()
        if not file_exists:
            raise Exception(f'Unable to create a document embeddings with id={document_id}. '
                            'Parsed document was not found')

        with open(parsed_file_path, "r", encoding="utf-8") as file:
            md_content = file.read()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.configuration.chunk_size,
            chunk_overlap=self.configuration.chunk_overlap,
            separators=["\n## ", "\n### ", "\n", " "]  # Prioritize splitting at markdown headings
        )

        chunks = splitter.split_text(md_content)
        self.vector_store_retriever.embed(chunks=chunks)