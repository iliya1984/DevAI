import os
from neo4j import GraphDatabase
from pydantic import BaseModel
from typing import Optional


class Neo4jConfiguration(BaseModel):
    url: str
    username: str
    password: str

    @staticmethod
    def from_env():
        url = os.environ['NEO4J_GRAPH_URL']
        user = os.environ['NEO4J_GRAPH_USER']
        password = os.environ['NEO4J_GRAPH_PASSWORD']

        return Neo4jConfiguration(
            url=url,
            username=user,
            password=password
        )


class Graph:
    def __init__(self):
        configuration = Neo4jConfiguration.from_env()

        uri = configuration.url
        username = configuration.username
        password = configuration.password

        self.driver = GraphDatabase.driver(uri, auth=(username, password))

    def write(self, transaction_fn, args):
        with (self.driver.session() as session):
            result = session.execute_write(transaction_fn, args)
            return result


class DocumentNode(BaseModel):
    url: Optional[str] = None
    storage_path: Optional[str] = None


class DocumentGraph:
    def __init__(self):
        self.graph = Graph()

    def create_node(self, node: DocumentNode):
        def create_node_tx(tx, args: DocumentNode):
            query = (
                "CREATE (d:Document {url: $url, storage_path: $storage_path})"
                "RETURN d"
            )
            result = tx.run(query, url=args.url, storage_path=args.storage_path)
            return result.single()

        node_result = self.graph.write(transaction_fn=create_node_tx, args=node)
        return node_result
