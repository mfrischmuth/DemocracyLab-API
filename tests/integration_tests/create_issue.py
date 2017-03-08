from __future__ import print_function
import sys
import uuid
import unittest

# add parent directory to path to allow importing app
from os.path import dirname, abspath
root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)

from app import app, graph
from shared import safe_json_loads


class CreateIssueTest(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.endpoint = "/api/issue"

    def parameters(self):
        self.name = "TestIssue{0}".format(uuid.uuid4())
        self.params = dict(
            issue_name=self.name,
            desc="Test Create Issue",
            values=["Value 1", "Value 2", "Value 3"],
            objectives=["Objective 1", "Objective 2", "Objective 3"],
            policies=["Policy 1", "Policy 2", "Policy 3"]
        )
        return self.params

    def test_basic(self):
        rv = self.app.post(self.endpoint, data=self.parameters())
        response = safe_json_loads(rv.data)
        self.check_status_code(rv.status_code)
        assert response["success"] == True
        self.issue_node = graph.nodes.find("Issue", response["issue_id"])
        assert self.issue_node, "No matching node found"
        assert self.issue_node.properties["name"] == self.name
        
        values=[]
        objectives=[]
        policies=[]
        for link in self.issue_node.match_outgoing():
            end_node = link.end_node
            if "Value" in end_node.labels:
                values.append(end_node['name'])
            if "Objective" in end_node.labels:
                objectives.append(end_node['name'])
            if "Policy" in end_node.labels:
                policies.append(end_node['name'])
        self.assertEqual(sorted(values),self.params["values"])
        self.assertEqual(sorted(objectives),self.params["objectives"])
        self.assertEqual(sorted(policies),self.params["policies"])

    def check_status_code(self, code):
        assert code == 200, "status code not 200"

    def tearDown(self):
        """
        delete value|objective|policy links and nodes
        then delete issue node
        """
        for link in self.issue_node.match_outgoing():
            end_node = link.end_node
            graph.graph.delete(link)
            graph.graph.delete(end_node)
        graph.graph.delete(self.issue_node)


if __name__ == '__main__':
    unittest.main()
