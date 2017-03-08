import sys
from os.path import dirname, abspath
import json
import unittest
import uuid
from random import randint
import py2neo

# add parent directory to path to allow importing app
root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)

from app import app, graph
from shared.neo_utils import Handler, User, Node, Rank


class MapTest(unittest.TestCase):
    
    strength = randint(0,99)
           
    def setUp(self):
        self.app = app.test_client()
        self.handler = Handler()
        self.user = User(self.handler)

    def tearDown(self):
        args = dict(start_node=self.map_node, rel_type="MAPS", bidirectional=True)
        for link in graph.graph.match(**args):
            self.handler.add_link(link)
        self.handler.clean_up()

    def postSetUp(self):
        self.data = self.parameters()
        self.map_id = "{0}-{1}".format(self.src.node_id, self.dst.node_id)
        
        # make sure each node is ranked by the user
        Rank(self.handler, self.user.node, self.src.node, 1)
        Rank(self.handler, self.user.node, self.dst.node, 1)
    
    def parameters(self):
        return dict(
            user_id=self.user.node_id,
            strength=self.strength,
            src_id = self.src.node_id,
            dst_id = self.dst.node_id
        )
        
    def check_status_code(self, code):
        self.assertEqual(code, 200, msg="status code not 200")

    def check_map(self):
        self.map_node = graph.nodes.find("Map", self.map_id)
        self.handler.add_node(self.map_node)
        self.assertIsNotNone(self.map_node, msg="Map node was not created")


class ValueObjectiveMapTest(MapTest):
    
    def setUp(self):
        super(ValueObjectiveMapTest, self).setUp()
        self.endpoint = "/api/map/value/objective"
        self.src = Node(self.handler, "Value")
        self.dst = Node(self.handler, "Objective")
        self.postSetUp() 

    def test(self):
        rv = self.app.post(self.endpoint, data=self.data)
        self.check_status_code(rv.status_code)
        self.check_map() 


class ObjectivePolicyMapTest(MapTest):
    
    def setUp(self):
        super(ObjectivePolicyMapTest, self).setUp()
        self.endpoint = "/api/map/objective/policy"
        self.src = Node(self.handler, "Objective")
        self.dst = Node(self.handler, "Policy")
        self.postSetUp()

    def test(self):
        rv = self.app.post(self.endpoint, data=self.data)
        self.check_status_code(rv.status_code)
        self.check_map() 


if __name__ == '__main__':
    unittest.main()
