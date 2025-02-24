from langchain_community.document_loaders import PyMuPDFLoader
from scipy.stats import bootstrap

from src.rag.parsing import (
    ParsingRequest,
    DocumentParser
 )
import dotenv
import unittest
from src.infra.di_module import Bootstrap

dotenv.load_dotenv()


class ParsingTests(unittest.TestCase):

    def test_parsing(self):
        bootstrap = Bootstrap()
        sut = bootstrap.container.document_parser()
        request = ParsingRequest(document_id='2109e24c-56ee-4519-b2f9-2c1d7473fe67')

        documents = sut.parse(request=request)
        self.assertIsNotNone(documents)


if __name__ == '__main__':
    unittest.main()
