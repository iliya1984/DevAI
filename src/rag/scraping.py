import os
import uuid

from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from src.data_access.graphs import DocumentGraph, DocumentTree, DocumentRelationship
from src.infra.configuration import ScrappingConfiguration

class IUrlFilter(ABC):
    @abstractmethod
    def apply(self, url: str) -> bool:
        pass

class WebPageScrappingRequest(BaseModel):
    url: str = []
    output_file_path: Optional[str] = None

class WebSiteScrappingRequest(BaseModel):
    site_name: str
    site_url : str
    url_filter: Optional[Any]
    persist_urls: bool = False

    @field_validator("url_filter")
    @classmethod
    def check_url_filter(cls, value):
        if value is not None and not isinstance(value, IUrlFilter):
            raise ValueError("url_filter must be an instance of IUrlFilter")
        return value

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
        output_file_path = request.output_file_path
        output_directory = str(Path(output_file_path).parent)

        os.makedirs(output_directory, exist_ok=True)

        import pdfkit
        pdfkit.from_url(url, output_file_path)

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
    def scrap(self, request: WebSiteScrappingRequest):
        pass

    @abstractmethod
    def get_links(self, url: str, persist: bool = False) -> List[str]:
        pass

class WebsiteScrapper(IWebSiteScrapper):
    def __init__(
            self,
            scrapper: IWebPageScrapper,
            graph: DocumentGraph,
            configuration: ScrappingConfiguration
    ):
        self.scrapper = scrapper
        self.graph = graph
        self.configuration = configuration

    def create_nodes_and_relationships(self, document_tree: DocumentTree):
        tree = document_tree.tree
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


    def scrap(self, request: WebSiteScrappingRequest):
        site_url = request.site_url
        site_name = request.site_name
        persist_urls = request.persist_urls
        url_filter = request.url_filter

        links = self.get_links(url=site_url, url_filter=url_filter, persist=persist_urls)
        tree = DocumentTree.from_url_list(urls=links, site_name=site_name)
        self.create_nodes_and_relationships(document_tree=tree)

        leaves = self.graph.get_leaves_by_site_name(site_name=site_name)
        for leaf in leaves:
            leaf_path = self.graph.get_leaf_path(leaf_id=leaf.id)
            docs_path = Path(self.configuration.storage_path).joinpath('docs')
            full_leaf_path = str(docs_path.joinpath(f'{leaf_path}.pdf'))
            leaf.storage_path = full_leaf_path
            self.graph.update_node(node=leaf)

            page_scrapping_request = WebPageScrappingRequest(
                url=leaf.url,
                output_file_path=leaf.storage_path
            )
            self.scrapper.scrap(request=page_scrapping_request)


        #TODO: Execute scrapping


    def get_links(self, url: str, url_filter: IUrlFilter = None, persist:bool=False) -> List[str]:
        links = self.scrapper.get_links(url=url)
        relevant_links = []
        if url_filter:
            for link in links:
                if url_filter.apply(link):
                    print(f'Skipping the {link} link')
                else:
                    relevant_links.append(link)

        else:
           relevant_links = links

        relevant_links_str = ''
        for link in relevant_links:
            relevant_links_str += link + '\n'

        if persist:
            output_directory = str(Path(self.configuration.storage_path) / "docs" / "langgraph" / "links.txt")
            Path(output_directory).parent.mkdir(parents=True, exist_ok=True)
            with open(output_directory, "w") as file:
                file.write(relevant_links_str)

        return relevant_links

class LanggraphUrlFilter(IUrlFilter):
    def apply(self, url: str) -> bool:
        filter_condition: bool = (
                'codelineno' in url
                or '#' in url
                or '/.' in url
                or not url.startswith('https://langchain-ai.github.io/langgraph/')
        )
        return filter_condition