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
from shared.neo_utils import Handler, User, Node, Link


class NodesTest(unittest.TestCase):

    SIZE = 3

    def setUp(self):
        self.app = app.test_client()
        self.handler = Handler()
    
    def tearDown(self):
        self.handler.clean_up()

    def parameters(self):
        return dict(filter_id=self.filter_id)
    
    def init_db(self, parent_type, child_type):
        """
        create parent and multiple children
        then create a link from parent to every child
        """
        self.parent = Node(self.handler, parent_type)
        self.children = [ Node(self.handler, child_type) for x in range(0, self.SIZE) ]
        for node in self.children:
            Link(self.handler, self.parent.node, node.node, child_type.upper())
    
    def check_status_code(self, code):
        self.assertEqual(code, 200, msg="status code not 200")

    def check_response(self, data):
        response = safe_json_loads(data)
        actual = [ node["node_id"] for node in response["nodes"] ]
        msg= "response nodes contain an invalid node_id"
        for node_id in [ node.node_id for node in self.children ]:
            self.assertIn(node_id, actual, msg=msg)
    
    def runner(self):
        rv = self.app.get(self.endpoint, data=self.data)
        self.check_status_code(rv.status_code)
        self.check_response(rv.data)


class CommunityNodesTest(NodesTest):

    def setUp(self):
        super(CommunityNodesTest, self).setUp()
        self.endpoint = "/api/community"
        self.init_db()
        self.data = {}
    
    def init_db(self):
        self.children = [ Node(self.handler, "Community") for x in range(0, self.SIZE) ]
   
    def test(self):
        self.runner()


class CommunityIssueNodesTest(NodesTest):

    def setUp(self):
        super(CommunityIssueNodesTest, self).setUp()
        self.endpoint = "/api/community/issue"
        self.init_db("Community", "Issue")
        self.filter_id = self.parent.node_id
        self.data = self.parameters()
    
    def test(self):
        self.runner()


class IssueValueNodesTest(NodesTest):

    def setUp(self):
        super(IssueValueNodesTest, self).setUp()
        self.endpoint = "/api/issue/value"
        self.init_db("Issue", "Value")
        self.filter_id = self.parent.node_id
        self.data = self.parameters()
    
    def test(self):
        self.runner()


class IssueObjectiveNodesTest(NodesTest):

    def setUp(self):
        super(IssueObjectiveNodesTest, self).setUp()
        self.endpoint = "/api/issue/objective"
        self.init_db("Issue", "Objective")
        self.filter_id = self.parent.node_id
        self.data = self.parameters()
    
    def test(self):
        self.runner()


class IssuePolicyNodesTest(NodesTest):

    def setUp(self):
        super(IssuePolicyNodesTest, self).setUp()
        self.endpoint = "/api/issue/policy"
        self.init_db("Issue", "Policy")
        self.filter_id = self.parent.node_id
        self.data = self.parameters()
    
    def test(self):
        self.runner()


if __name__ == '__main__':
    unittest.main()
