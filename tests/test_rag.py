import unittest
from src.rag.vector_store import ChromaDbVectorStoreRetriever, docs
from src.rag.scraping import LanggraphDocScrapper, WebPageScrapper, WebPageScrappingRequest
from src.data_access.graphs import DocumentGraph
from pathlib import Path
import dotenv

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

    def test_link_retrieval(self):
        # sut = WebPageScrapper()
        # url = 'https://langchain-ai.github.io/langgraph/'
        # links = sut.get_links(url=url)
        #
        # relevant_links = ''
        # for link in links:
        #     if ('codelineno' in link
        #             or '#' in link
        #             or '.' in link
        #             or not link.startswith('https://langchain-ai.github.io/langgraph/')
        #     ):
        #         print(f'Skipping the {link} link')
        #     else:
        #         relevant_links += link + '\n'
        #
        # output_directory = str(Path.cwd() / "docs" / "langgraph" / "links.txt")
        # with open(output_directory, "w") as file:
        #     file.write(relevant_links)

        sut = LanggraphDocScrapper(
            scrapper=WebPageScrapper(),
            graph=DocumentGraph()
        )

        result = sut.scrap()
        #self.assertIsNotNone(links)

if __name__ == '__main__':
    unittest.main()
