import unittest
from src.rag.vector_store import ChromaDbVectorStoreRetriever, docs
from src.rag.scraping import (
    WebsiteScrapper,
    WebPageScrapper,
    WebPageScrappingRequest,
    WebSiteScrappingRequest,
    LanggraphUrlFilter
)
from src.data_access.graphs import DocumentGraph
from pathlib import Path
import dotenv
from src.infra.di_module import Bootstrap

dotenv.load_dotenv()

class LLMTests(unittest.TestCase):

    def test_vector_search(self):
        ChromaDbVectorStoreRetriever.from_docs(docs)
        i = 1

    def test_web_scrapping(self):
        sut = WebPageScrapper()

        output_directory = str(Path.cwd() / "docs" / "langgraph" / "home.pdf")
        request = WebPageScrappingRequest(
            url='https://langchain-ai.github.io/langgraph/',
            output_directory=output_directory
        )
        sut.scrap(request=request)

    def test_website_scrapping(self):
        bootstrap = Bootstrap()
        site_url = 'https://langchain-ai.github.io/langgraph/'
        site_name = 'langgraph'

        request = WebSiteScrappingRequest(
            site_name=site_name,
            site_url=site_url,
            persist_urls=True,
            url_filter=LanggraphUrlFilter()
        )

        sut = bootstrap.container.web_site_scrapper()

        result = sut.scrap(request=request)
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
