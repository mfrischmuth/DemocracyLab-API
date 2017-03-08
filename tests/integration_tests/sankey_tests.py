from __future__ import print_function
import sys
import os
import json
from os.path import dirname, abspath
import unittest

# add parent directory to path to allow importing app
root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)

from shared import safe_json_loads
from app import app, CQLDIR, graph


class SankeyTest(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.issue = "i1"

    def test_basic(self):
        rv = self.app.get("/api/sankey", data=dict(issue_id=self.issue))
        self.assertIs(rv.status_code, 200)
        data = safe_json_loads(rv.data)
        self.assertIn("links", data)
        self.assertIn("nodes", data)


if __name__ == '__main__':
    unittest.main()
