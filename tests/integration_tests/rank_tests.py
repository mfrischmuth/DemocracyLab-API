import sys
from os.path import dirname, abspath
import unittest
import uuid
from random import randint

# add parent directory to path to allow importing app
root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)

from app import app, graph
from shared import safe_json_loads
from shared.neo_utils import Handler, User, Node


class RankTest(unittest.TestCase):
    
    rank = randint(0, 99)
           
    def setUp(self):
        self.app = app.test_client()
        self.handler = Handler()
        self.user = User(self.handler)
        self.issue_id = str(uuid.uuid4())
    
    def tearDown(self):
        self.handler.clean_up()

    def parameters(self):
        return dict(
            user_id=self.user.node_id,
            node_id=self.node.node_id,
            rank=self.rank,
            issue_id=self.issue_id,
        )
   
    def find_link(self):
        link = graph.links.find(self.user.node, self.node.node, "RANKS")
        self.handler.add_link(link)
        return link

    def check_rank(self):
        link = self.find_link()
        assert link, "failed to find link"
        self.assertEqual(link.properties["rank"], self.rank)

    def check_status_code(self, code):
        assert code == 200, "status code not 200"

    def check_response(self, expected, data):
        response = safe_json_loads(data)
        error = "expecting: {0}, actual: {1}".format(expected, response)
        assert response == expected, error

    def runner(self):
        rv = self.app.post(self.endpoint, data=self.data)
        expected = dict(success=True)
        self.check_status_code(rv.status_code)
        self.check_response(expected, rv.data)
        self.check_rank()


class ValueRankTest(RankTest):
    
    def setUp(self):
        super(ValueRankTest, self).setUp()
        self.node = Node(self.handler, "Value")
        self.endpoint = "/api/rank/value"
        self.data = self.parameters()

    def test(self):
        self.runner()


class ObjectiveRankTest(RankTest):
    
    def setUp(self):
        super(ObjectiveRankTest, self).setUp()
        self.node = Node(self.handler, "Objective")
        self.endpoint = "/api/rank/objective"
        self.data = self.parameters()

    def test(self):
        self.runner()


class PolicyRankTest(RankTest):
    
    def setUp(self):
        super(PolicyRankTest, self).setUp()
        self.node = Node(self.handler, "Policy")
        self.endpoint = "/api/rank/policy"
        self.data = self.parameters()

    def test(self):
        self.runner()


class NoUserRankTest(RankTest):
    
    def setUp(self):
        self.app = app.test_client()
        self.handler = Handler()
        self.user_id = str(uuid.uuid4())
        self.node = Node(self.handler, "Value")
        self.endpoint = "/api/rank/value"
        self.data = dict(
            user_id=self.user_id,
            node_id=self.node.node_id,
            rank=self.rank,
            issue_id=str(uuid.uuid4())
        )
    
    def test(self):
        rv = self.app.post(self.endpoint, data=self.data)
        expected = dict(success=False, error="invalid user_id")
        self.check_status_code(rv.status_code)
        self.check_response(expected, rv.data)


class NoNodeRankTest(RankTest):
    
    def setUp(self):
        self.app = app.test_client()
        self.handler = Handler()
        self.user = User(self.handler)
        self.node_id = str(uuid.uuid4())
        self.endpoint = "/api/rank/value"
        self.data = dict(
            user_id=self.user.node_id,
            node_id=self.node_id,
            rank=self.rank,
            issue_id=str(uuid.uuid4())
        )
    
    def test(self):
        rv = self.app.post(self.endpoint, data=self.data)
        expected = dict(success=False, error="invalid node_id")
        self.check_status_code(rv.status_code)
        self.check_response(expected, rv.data)


class UpdateRankTest(RankTest):
    
    def setUp(self):
        super(UpdateRankTest, self).setUp()
        self.node = Node(self.handler, "Value")
        self.endpoint = "/api/rank/value"
        self.data = self.parameters()
    
    def test(self):
        # rank node
        rv = self.app.post(self.endpoint, data=self.data)
        expected = dict(success=True)
        self.check_status_code(rv.status_code)
        self.check_response(expected, rv.data)
        self.check_rank()

        # update
        self.rank = randint(0, 99)
        self.data = self.parameters()
        
        # re-rank
        rv = self.app.post(self.endpoint, data=self.data)
        self.check_status_code(rv.status_code)
        self.check_response(expected, rv.data)
        self.check_rank()


if __name__ == '__main__':
    unittest.main()
