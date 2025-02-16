import unittest
from src.rag.vector_store import embeddings_model

class LLMTests(unittest.TestCase):

    def test_vector_search(self):
        vector = embeddings_model.aembed_query('Test my embedding model')
        self.assertIsNotNone(vector)

if __name__ == '__main__':
    unittest.main()
