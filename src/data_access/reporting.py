from elasticsearch import Elasticsearch
from datetime import datetime
from abc import ABC, abstractmethod
from src.infra.configuration import ElasticsearchConfiguration

class IReportClient(ABC):
    @abstractmethod
    def report(self, record: dict):
        pass

class ReportClient(IReportClient):
    def __init__(self, configuration: ElasticsearchConfiguration):
        host = configuration.endpoint
        username = configuration.username
        password = configuration.password
        self.es = Elasticsearch(
            [host],
            basic_auth=(username, password),
            verify_certs=False
        )


    def report(self, record: dict):
        response = self.es.index(index="coding-assistant", document=record)
        return response