from dependency_injector import  containers, providers
from dependency_injector.containers import DeclarativeContainer
from src.rag.vector_store import ChromaDbVectorStoreRetriever
from src.infra.configuration import ConfigurationManager
from src.inference.chatbots import OllamaChatClient
from src.infra.logging_infra import logger
from src.data_access.graphs import Graph, DocumentGraph
from src.data_access.reporting import ReportClient

class InferenceDIContainer(DeclarativeContainer):
    config = providers.Configuration()

    logger = providers.Singleton(lambda: logger)

    neo4j_config = providers.Singleton(config.neo4j)
    neo4j_graph = providers.Singleton(
        Graph,
        configuration=neo4j_config
    )

    document_graph = providers.Singleton(
        DocumentGraph,
        graph=neo4j_graph
    )

    elasticsearch_config = providers.Singleton(config.elasticsearch)
    report_client = providers.Singleton(
        ReportClient,
        configuration=elasticsearch_config
    )

    chat_vector_db_config = providers.Singleton(config.chat_vector_db)
    chat_embedding_model_config = providers.Singleton(config.chat_embedding_model)
    chat_vector_store_retriever = providers.Singleton(
        ChromaDbVectorStoreRetriever,
        chroma_db_config=chat_vector_db_config,
        huggingface_embed_config=chat_embedding_model_config,
        logger=logger
    )

    chat_config = providers.Singleton(config.chat)
    chat_client = providers.Singleton(
        OllamaChatClient,
        vector_store_retriever=chat_vector_store_retriever,
        report_client=report_client,
        configuration=chat_config
    )


class InferenceBootstrap:
    def __init__(self):
        self.configuration = ConfigurationManager().get()
        self.container = InferenceDIContainer()

        self.container.config.neo4j.from_value(self.configuration.neo4j_graph)
        self.container.config.elasticsearch.from_value(self.configuration.elasticsearch)
        self.container.config.embedding.from_value(self.configuration.embedding)
        self.container.config.chat.from_value(self.configuration.chat)
        self.container.config.chat_vector_db.from_value(self.configuration.chat.chroma_db)
        self.container.config.chat_embedding_model.from_value(self.configuration.chat.huggingface_embedding)