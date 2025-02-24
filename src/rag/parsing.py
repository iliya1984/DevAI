import fitz
import io
from abc import ABC, abstractmethod
from pydantic import BaseModel
import pymupdf4llm
from pymupdf import Document
from src.data_access.graphs import DocumentGraph
from pathlib import Path
from src.infra.configuration import ParsingConfiguration
import os

class ParsingRequest(BaseModel):
    document_id: str


class IParser(ABC):
    @abstractmethod
    def parse(self, request: ParsingRequest):
        pass

class DocumentParser(IParser):
    def __init__(self, graph: DocumentGraph, configuration: ParsingConfiguration):
        self.graph = graph
        self.configuration = configuration

    def parse(self, request: ParsingRequest):
        document_id = request.document_id
        document_node = self.graph.get_document_node_by_id(document_id=document_id)

        if document_node is None:
            raise Exception(f'Unable to parse a document with id={document_id}. Document was not found')

        leaf_path = self.graph.get_leaf_path(leaf_id=document_id)
        parsed_docs_path = Path(self.configuration.storage_path).joinpath('parsed_docs')
        parsed_file_path = str(parsed_docs_path.joinpath(f'{leaf_path}.md'))
        document_node.parsing_storage_path = parsed_file_path
        self.graph.update_node(node=document_node)

        if document_node.storage_path is None:
            raise Exception(f'Unable to parse a document with id={document_id}. Storage path was not found')

        document_path = document_node.storage_path
        with open(document_path, "rb") as f:
            document_bytes = f.read()

        document_stream = io.BytesIO(document_bytes)
        document: Document = fitz.open(
            stream=document_stream,
            filetype='pdf'
        )

        parsed_content = pymupdf4llm.to_markdown(document, show_progress=True)

        output_directory = str(Path(parsed_file_path).parent)
        os.makedirs(output_directory, exist_ok=True)

        with open(parsed_file_path, "w", encoding="utf-8") as file:
            file.write(parsed_content)

        return parsed_content
