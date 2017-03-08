import sys
from os.path import dirname, abspath
import unittest

# add parent directory to path to allow importing app
root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)

from app import graph
from shared.neo_utils import Handler, Node, Link, User, Rank


class NodesFindAllTest(unittest.TestCase):

    def setUp(self):
        """
        Tests for findall() and findall_withUserID() 
        Create 1 user, 1 issue and 5 value nodes
        User ranks values 0, 3, 4
        Issue has values 0, 1, 4
        """
        self.handler = Handler()
        self.issue = Node(self.handler, "TestIssue")
        self.nodes = [Node(self.handler, "TestValue") for _ in range(0, 5)]
        self.user = User(self.handler)
        Link(self.handler, self.issue.node, self.nodes[0].node, "HAS") 
        Link(self.handler, self.issue.node, self.nodes[1].node, "HAS")
        Link(self.handler, self.issue.node, self.nodes[4].node, "HAS")		
        Rank(self.handler, self.user.node, self.nodes[0].node, 1)
        Rank(self.handler, self.user.node, self.nodes[3].node, 2)
        Rank(self.handler, self.user.node, self.nodes[4].node, -1)

    def tearDown(self):
        self.handler.clean_up()

    def test_findall(self):
        """
        test that all TestValue nodes are returned
        """
        node_ids = [node.node_id for node in self.nodes]
        nodes = graph.nodes.find_all("TestValue")
        for node in nodes:
            self.assertIn(node["node_id"], node_ids)

    def test_parent_issue_findall(self):
        """
        test that only TestValue nodes 0, 1, 4 are returned as the other nodes
        do not have a link from the TestIssue node
        """
        node_in_ids = sorted([self.nodes[0].node_id, self.nodes[1].node_id,
                             self.nodes[4].node_id])
        args = dict(parent_id=self.issue.node_id, parent_label="TestIssue")
        answer_ids = sorted([node["node_id"] for node in
                             graph.nodes.find_all("TestValue", **args)])
        self.assertEqual(node_in_ids, answer_ids)

    def test_parent_issue_findall_with_user_id(self):
        """
        test that only TestValue 2 nodes 0, 4 are returned as the other nodes do
        not have a link from the TestIssue node or are not ranked by the user
        """
        node_in_ids = sorted([self.nodes[0].node_id, self.nodes[4].node_id])
        args = dict(parent_id=self.issue.node_id, parent_label="TestIssue")
        answer_nodes = graph.nodes.find_all_with_user_id(
            "TestValue", self.user.node_id, **args)
    # for node in nodes:
    #     self.assertIn(node["node_id"], nodeIn_ids)
    #     self.assertNotIn(node["node_id"], nodeNotIn_ids)
        answer_ids = sorted([node["node_id"] for node in answer_nodes])
        self.assertEqual(node_in_ids, answer_ids)


if __name__ == '__main__':
    unittest.main()
