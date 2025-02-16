import unittest
from src.rag.vector_store import ChromaDbVectorStoreRetriever, docs

class LLMTests(unittest.TestCase):

    def test_vector_search(self):
        ChromaDbVectorStoreRetriever.from_docs(docs)
        i = 1

if __name__ == '__main__':
    unittest.main()
