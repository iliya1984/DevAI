import unittest
import uuid

from src.data_access.graphs import DocumentGraph
import dotenv
from src.infra.configuration import ConfigurationManager
from elasticsearch import Elasticsearch
from datetime import datetime


dotenv.load_dotenv()

class GraphTests(unittest.TestCase):
    def test_get_leaves(self):
        sut = DocumentGraph()
        #result = sut.get_leaves_by_site_name(site_name='langgraph')
        result = sut.get_leaf_path(leaf_id='52a04290-a1e6-4ac1-9339-8bedb44193e4')
        self.assertIsNotNone(result)

    def test_configuration(self):
        configuration_manager = ConfigurationManager()
        config = configuration_manager.get()
        self.assertIsNotNone(config)


if __name__ == '__main__':
    unittest.main()