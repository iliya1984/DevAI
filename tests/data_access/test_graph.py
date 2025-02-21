import unittest
from src.data_access.graphs import DocumentGraph
import dotenv

dotenv.load_dotenv()

class GraphTests(unittest.TestCase):
    def test_get_leaves(self):
        sut = DocumentGraph()
        result = sut.get_leaves_by_site_name(site_name='langgraph')
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()