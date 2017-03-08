from __future__ import print_function
import sys
import os
from os.path import dirname, abspath
import unittest

# add parent directory to path to allow importing app
root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)


from app import app, CQLDIR, graph

"""
class GraphSentimentTest(unittest.TestCase):
          
    def test_basic(self):
        filename = os.path.join(CQLDIR, "value_objective_sentiment.cql")
        results = graph.execute_raw(filename)


class HandlerSentimentTest(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()

    def test_basic(self):
        self.app.get("/api/sentiment")
"""

if __name__ == '__main__':
    unittest.main()
