import pdfkit
from pydantic import BaseModel
from typing import Optional, List
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from src.data_access.graphs import DocumentGraph, DocumentNode
from langchain_core.documents import Document


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



    def scrap(self):
        url = 'https://langchain-ai.github.io/langgraph/'
        name = 'langgraph'

        node = DocumentNode(
            url=url,
            storage_path='my_path'
        )
        result = self.graph.create_node(node=node)

        links = self.get_links(url=url)

        first_link = links[0]


        #for url in links:




    def get_links(self, url: str, persist:bool=False) -> List[str]:
        links = self.scrapper.get_links(url=url)

        relevant_links = []
        relevant_links_str = ''

        for link in links:
            if ('codelineno' in link
                    or '#' in link
                    or '.' in link
                    or ':' in link
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