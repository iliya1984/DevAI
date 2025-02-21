import os
from neo4j import GraphDatabase, Result
from pydantic import BaseModel
from typing import Optional, List
from treelib import Node, Tree
from urllib.parse import urlparse
import uuid

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

    def select(self, query: str, args: dict):
        with self.driver.session() as session:
            result = session.run(query, args)
            return [dict(record) for record in result]

    def write(self, transaction_fn, args):
        with (self.driver.session() as session):
            result = session.execute_write(transaction_fn, args)
            return result


class DocumentNode(BaseModel):
    id: str
    name: Optional[str] = None
    url: Optional[str] = None
    storage_path: Optional[str] = None
    site_name: Optional[str] = None
    is_root: bool = False
    is_leaf: bool = False


class DocumentRelationship(BaseModel):
    id: str
    start_document_id: str
    end_document_id: str


class DocumentTree:
    def __init__(self, tree):
        self.tree = tree

    @staticmethod
    # Function to extract path components
    def __extract_path_components(url):
        parsed_url = urlparse(url)
        # Split the path and filter out empty components
        return [comp for comp in parsed_url.path.split('/') if comp]

    @staticmethod
    def __mark_leaf_nodes(tree: Tree):
        for node in tree.all_nodes():
            is_leaf = not tree.children(node.identifier)

            tree_node = tree.get_node(node.identifier)
            if tree_node.data:
                tree_node.data.is_leaf = is_leaf

    @staticmethod
    def from_url_list(urls: list, site_name: str):
        tree = Tree()
        root_id = str(uuid.uuid4())
        root_node = DocumentNode(id=root_id, name='root', site_name=site_name, is_root=True)
        tree.create_node(tag="root", identifier=root_id, data=root_node)

        # Dictionary to keep track of added nodes
        added_nodes = {"root": root_id}

        # Build the tree structure
        for url in urls:
            components = DocumentTree.__extract_path_components(url)
            parent_id = root_id
            path = "root"
            for comp in components:
                path = f"{path}/{comp}"
                if path not in added_nodes:
                    node_id = str(uuid.uuid4())
                    node_data = DocumentNode(id=node_id, name=comp, url=url, site_name=site_name)
                    tree.create_node(tag=comp, identifier=node_id, parent=parent_id, data=node_data)
                    added_nodes[path] = node_id
                parent_id = added_nodes[path]

        DocumentTree.__mark_leaf_nodes(tree)
        return DocumentTree(tree=tree)

class DocumentGraph:
    def __init__(self):
        self.graph = Graph()

    def get_leaves_by_site_name(self, site_name: str) -> List[DocumentNode]:
        query = """
            MATCH (n:Document:DocumentLeaf {site_name: $site_name}) 
            RETURN n.id AS id, n.name AS name, n.url AS url, 
                   n.storage_path AS storage_path, n.site_name AS site_name, 
                   true AS is_leaf
            """

        result = self.graph.select(query=query, args={'site_name' : site_name})
        leaves = [DocumentNode(**record) for record in result]
        return leaves

    def create_relationship(self, relationship: DocumentRelationship):
        def create_relationship_tx(tx, args: DocumentRelationship):
            query = """
                            MATCH (p:Document {id: $start_document_id})
                            MATCH (c:Document {id: $end_document_id})
                            MERGE (p)-[:HAS_LINK_TO]->(c)
                            """
            result = tx.run(
                query,
                start_document_id=args.start_document_id,
                end_document_id=args.end_document_id
            )
            return result.single()

        relationship_result = self.graph.write(transaction_fn=create_relationship_tx, args=relationship)
        return relationship_result

    def create_node(self, node: DocumentNode):
        def create_node_tx(tx, args: DocumentNode):
            tags = []
            if args.is_root:
                tags.append('DocumentGroup')
            if args.is_leaf:
                tags.append('DocumentLeaf')

            dynamic_labels = ":".join(tags) if tags else ""

            query = f"""
            CREATE (d:Document{':' + dynamic_labels if dynamic_labels else ''} {{
                id: $id,
                name: $name,
                site_name: $site_name,
                url: $url,
                storage_path: $storage_path
            }})
            RETURN d
            """

            params = args.model_dump()
            result = tx.run(query, **params)
            return result.single()

        node_result = self.graph.write(transaction_fn=create_node_tx, args=node)
        return node_result
