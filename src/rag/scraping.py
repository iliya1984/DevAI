import uuid

import pdfkit
from pydantic import BaseModel
from typing import Optional, List
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from src.data_access.graphs import DocumentGraph, DocumentNode, DocumentRelationship
from langchain_core.documents import Document
from urllib.parse import urlparse
from treelib import Node, Tree
# List of URLs

# Function to extract path components
def extract_path_components(url):
    parsed_url = urlparse(url)
    # Split the path and filter out empty components
    return [comp for comp in parsed_url.path.split('/') if comp]


def build_tree_from_url_list(urls: list, site_name: str):
    tree = Tree()
    root_id = str(uuid.uuid4())
    root_node = DocumentNode(id=root_id, name='root', site_name=site_name)
    tree.create_node(tag="root", identifier=root_id, data=root_node)

    # Dictionary to keep track of added nodes
    added_nodes = {"root": root_id}

    # Build the tree structure
    for url in urls:
        components = extract_path_components(url)
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
    return tree

class WebPageScrappingRequest(BaseModel):
    url: str = []
    output_file_path: Optional[str] = None

class IWebPageScrapper(ABC):
    @abstractmethod
    def scrap(self, request: WebPageScrappingRequest):
        pass

    @abstractmethod
    def get_links(self, url: str, persist:bool=False) -> List[str]:
        pass

class WebPageScrapper(IWebPageScrapper):

    def scrap(self, request: WebPageScrappingRequest):
        url = request.url
        output_directory = request.output_directory
        pdfkit.from_url(url, output_directory)

    def get_links(self, url: str, persist:bool=False) -> List[str]:
        """Extracts all links from the webpage"""
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all anchor tags and get their href
        links = [a["href"] for a in soup.find_all("a", href=True)]

        # Filter out only relevant absolute URLs
        base_url = url if url.endswith("/") else url + "/"
        full_links = [link if link.startswith("http") else base_url + link.lstrip("/") for link in links]

        return list(set(full_links))

class IWebSiteScrapper(ABC):
    @abstractmethod
    def scrap(self):
        pass

    @abstractmethod
    def get_links(self, url: str, persist: bool = False) -> List[str]:
        pass

class LanggraphDocScrapper(IWebSiteScrapper):
    def __init__(self, scrapper: IWebPageScrapper, graph: DocumentGraph):
        self.scrapper = scrapper
        self.graph = graph

    def create_nodes_and_relationships(self, tree: Tree):
        for tree_node in tree.all_nodes_itr():
            node = tree_node.data
            self.graph.create_node(node=node)

            if tree_node.is_root():
                continue

            parent_tree_node = tree.parent(tree_node.identifier)
            parent_node = parent_tree_node.data
            relationship = DocumentRelationship(
                start_document_id=parent_node.id,
                end_document_id=node.id,
                id = str(uuid.uuid4())
            )
            self.graph.create_relationship(relationship=relationship)

    def scrap(self):
        site_url = 'https://langchain-ai.github.io/langgraph/'
        site_name = 'langgraph'
        links = self.get_links(url=site_url)
        tree = build_tree_from_url_list(urls=links, site_name=site_name)
        self.create_nodes_and_relationships(tree=tree)
        i = 1



    def get_links(self, url: str, persist:bool=False) -> List[str]:
        links = self.scrapper.get_links(url=url)

        relevant_links = []
        relevant_links_str = ''

        for link in links:
            if ('codelineno' in link
                    or '#' in link
                    or '/.' in link
                    or not link.startswith('https://langchain-ai.github.io/langgraph/')
            ):
                print(f'Skipping the {link} link')
            else:
                relevant_links.append(link)
                relevant_links_str += link + '\n'

        if persist:
            output_directory = str(Path.cwd() / "docs" / "langgraph" / "links.txt")
            with open(output_directory, "w") as file:
                file.write(relevant_links_str)

        return relevant_links