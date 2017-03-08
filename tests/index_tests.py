import six
import os
import unittest
import sys

# add parent directory to path to import app
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root)

from app import app, graph
from shared import safe_json_loads


class IndexTests(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
    
    def test_index(self):
        rv = self.app.get('/')
        expected = "ROOT API"
        if isinstance(rv.data, six.string_types):
            response = rv.data
        else:
            response = rv.data.decode('utf-8')
        self.assertEqual(response, expected)

    def test_api_index(self):
        rv = self.app.get('/api') 
        expected = dict(response="API Index")
        response = safe_json_loads(rv.data)
        self.assertEqual(response, expected)


if __name__ == '__main__':
    unittest.main()
