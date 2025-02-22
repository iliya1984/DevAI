from dependency_injector import  containers, providers
from dependency_injector.containers import DeclarativeContainer
import logging
from src.infra.configuration import ConfigurationManager
from src.data_access.graphs import Graph, DocumentGraph
from src.rag.scraping import WebPageScrapper, WebsiteScrapper

def create_logger(logger_name) -> logging.Logger:
    return logging.getLogger(name=logger_name)

logger = create_logger('DevAI')

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


class Bootstrap:
    def __init__(self):
        self.configuration = ConfigurationManager().get()
        self.container = DIContainer()

        self.container.config.neo4j.from_value(self.configuration.neo4j_graph)
        self.container.config.scrapping.from_value(self.configuration.scrapping)
