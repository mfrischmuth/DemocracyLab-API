import sys
from os.path import dirname, abspath
import unittest
import uuid

import py2neo

# add parent directory to path to allow importing app
root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)

from app import app, graph
from shared import safe_json_loads
from shared.neo_utils import Handler, User, Node


class NodeTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.handler = Handler()
    
    def tearDown(self):
        self.handler.clean_up()

    def runner(self):
        data = dict(id=self.node.node_id)
        rv = self.app.get(self.endpoint, data=data)
        response = safe_json_loads(rv.data)
        contains_id = set(data.items()).issubset(set(response.items()))
        self.assertTrue(contains_id, msg="response does not contain node id")


class GetUserTest(NodeTest):

    def setUp(self):
        super(GetUserTest, self).setUp()
        self.node = User(self.handler)
        self.endpoint = "/api/user"

    def test(self):
        self.runner()


class GetIssueTest(NodeTest):

    def setUp(self):
        super(GetIssueTest, self).setUp()
        self.node = Node(self.handler, "Issue")
        self.endpoint = "/api/issue"

    def test(self):
        self.runner()


class GetValueTest(NodeTest):

    def setUp(self):
        super(GetValueTest, self).setUp()
        self.node = Node(self.handler, "Value")
        self.endpoint = "/api/value"

    def test(self):
        self.runner()


class GetObjectiveTest(NodeTest):

    def setUp(self):
        super(GetObjectiveTest, self).setUp()
        self.node = Node(self.handler, "Objective")
        self.endpoint = "/api/objective"

    def test(self):
        self.runner()


class GetPolicyTest(NodeTest):

    def setUp(self):
        super(GetPolicyTest, self).setUp()
        self.node = Node(self.handler, "Policy")
        self.endpoint = "/api/policy"

    def test(self):
        self.runner()


if __name__ == '__main__':
    unittest.main()
