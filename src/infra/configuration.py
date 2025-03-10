import os
import json
from pydantic import BaseModel
from typing import Optional
import dotenv
from abc import ABC, abstractmethod

dotenv.load_dotenv()

class Neo4jConfiguration(BaseModel):
    url: str
    username: str
    password: str

class ElasticsearchConfiguration(BaseModel):
    endpoint: str
    username: str
    password: str

class ScrappingConfiguration(BaseModel):
    storage_path: str

class ParsingConfiguration(BaseModel):
    storage_path: str

class HuggingFaceEmbeddingConfiguration(BaseModel):
    model_name: str
    persist_directory: str

class ChromaDBConfiguration(BaseModel):
    persist_directory: str
    collection_name: str

class EmbeddingConfiguration(BaseModel):
    huggingface_embedding: Optional[HuggingFaceEmbeddingConfiguration] = None
    chunk_size: int = 1000
    chunk_overlap: int = 100
    chroma_db: Optional[ChromaDBConfiguration] = None

class OllamaConfiguration(BaseModel):
    host: str
    version: str

class CompletionConfiguration(BaseModel):
    chunk_number: int = 5

class ChatConfiguration(BaseModel):
    ollama: Optional[OllamaConfiguration] = None
    huggingface_embedding: Optional[HuggingFaceEmbeddingConfiguration] = None
    chroma_db: Optional[ChromaDBConfiguration] = None
    completion: Optional[CompletionConfiguration] = None


class Configuration(BaseModel):
    neo4j_graph: Optional[Neo4jConfiguration] = None
    elasticsearch: Optional[ElasticsearchConfiguration] = None
    scrapping: Optional[ScrappingConfiguration] = None
    parsing: Optional[ParsingConfiguration] = None
    embedding: Optional[EmbeddingConfiguration] = None
    chat: Optional[ChatConfiguration] = None

class ConfigurationManager:

    def replace_secrets(self, obj):
        """
        Recursively traverse the JSON object and replace secret placeholders with environment variable values.
        """
        if isinstance(obj, dict):
            return {k: self.replace_secrets(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.replace_secrets(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("$secret(") and obj.endswith(")"):
            # Extract the environment variable name
            env_var = obj[8:-1]
            # Retrieve the environment variable value
            return os.environ.get(env_var, f"Environment variable '{env_var}' not found")
        else:
            return obj

    def get(self) -> Configuration:
        config_file_path = os.environ['CONFIGURATION_FILE_PATH']

        with open(config_file_path, 'r') as file:
            data = json.load(file)
            data = self.replace_secrets(data)
            config = Configuration(**data)
            return config


