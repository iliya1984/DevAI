from dependency_injector import  containers, providers
from dependency_injector.containers import DeclarativeContainer
import logging
from src.infra.configuration import ConfigurationManager
from src.data_access.graphs import Graph, DocumentGraph
from src.rag.scraping import WebPageScrapper, WebsiteScrapper
from src.rag.parsing import DocumentParser
from src.rag.vector_store import ChromaDbVectorStoreRetriever
from src.rag.embedding import DocumentEmbedder
from src.inference.chatbots import OllamaChatClient
from src.infra.logging_infra import logger


class DIContainer(DeclarativeContainer):
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

    scrapping_config = providers.Singleton(config.scrapping)
    web_page_scrapper = providers.Singleton(WebPageScrapper)
    web_site_scrapper = providers.Singleton(
        WebsiteScrapper,
        scrapper=web_page_scrapper,
        graph=document_graph,
        configuration=scrapping_config
    )

    parsing_config = providers.Singleton(config.parsing)
    document_parser = providers.Singleton(
        DocumentParser,
        graph=document_graph,
        configuration=parsing_config
    )

    embedding_vector_db_config = providers.Singleton(config.embedding_vector_db)
    embedding_model_config = providers.Singleton(config.embedding_model)

    embedding_vector_store_retriever = providers.Singleton(
        ChromaDbVectorStoreRetriever,
        chroma_db_config=embedding_vector_db_config,
        huggingface_embed_config=embedding_model_config,
        logger=logger
    )
    embedding_config = providers.Singleton(config.embedding)

    document_embedder = providers.Singleton(
        DocumentEmbedder,
        graph=document_graph,
        vector_store_retriever=embedding_vector_store_retriever,
        configuration=embedding_config,
        logger=logger
    )



class RagPipelineBootstrap:
    def __init__(self):
        self.configuration = ConfigurationManager().get()
        self.container = DIContainer()

        self.container.config.neo4j.from_value(self.configuration.neo4j_graph)
        self.container.config.scrapping.from_value(self.configuration.scrapping)
        self.container.config.parsing.from_value(self.configuration.parsing)
        self.container.config.embedding.from_value(self.configuration.embedding)
        self.container.config.chat.from_value(self.configuration.chat)
        self.container.config.embedding_vector_db.from_value(self.configuration.embedding.chroma_db)
        self.container.config.embedding_model.from_value(self.configuration.embedding.huggingface_embedding)


