import pdfkit
from pydantic import BaseModel
from typing import Optional, List
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup


class WebScrappingRequest(BaseModel):
    url: str
    output_directory: Optional[str] = None

class IWebScrapper(ABC):
    @abstractmethod
    def scrap(self, request: WebScrappingRequest):
        pass

    @abstractmethod
    def get_links(self, url: str) -> List[str]:
        pass

class WebScrapper(IWebScrapper):

    def scrap(self, request: WebScrappingRequest):
        url = request.url
        output_directory = request.output_directory
        pdfkit.from_url(url, output_directory)

    def get_links(self, url: str) -> List[str]:
        """Extracts all links from the webpage"""
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract all anchor tags and get their href
        links = [a["href"] for a in soup.find_all("a", href=True)]

        # Filter out only relevant absolute URLs
        base_url = url if url.endswith("/") else url + "/"
        full_links = [link if link.startswith("http") else base_url + link.lstrip("/") for link in links]

        return list(set(full_links))
