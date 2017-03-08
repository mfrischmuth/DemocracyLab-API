import sys
from os.path import dirname, abspath
import unittest
import uuid
from random import randint
import py2neo

# add parent directory to path to allow importing app
root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)

from app import app, graph
from app.mod_api.auth import Authenticate
from shared import safe_json_loads
from shared.neo_utils import Handler, User, Node


PASSWORD = "password"


class LoginTests(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.handler = Handler()
        self.user = User(self.handler)
        self.endpoint = "/api/login"
   
    def tearDown(self):
        self.handler.clean_up()

    def parameters(self):
        return dict(
            username=self.user.node_id,
            password=PASSWORD
        )

    def check_status_code(self, code):
        assert code == 200, "status code not 200"

    def test_valid(self):
        rv = self.app.post(self.endpoint, data=self.parameters())
        self.check_status_code(rv.status_code)
        self.assertTrue(safe_json_loads(rv.data)["success"], msg="success not true")
    
    def test_invalid_username(self):
        data = self.parameters()
        data["username"] = str(uuid.uuid4())
        rv = self.app.post(self.endpoint, data=data)
        self.check_status_code(rv.status_code)
        msg = "login should have failed, invalid username"
        self.assertFalse(safe_json_loads(rv.data)["success"], msg=msg)

    def test_invalid_password(self):
        data = self.parameters()
        data["password"] = str(uuid.uuid4())
        rv = self.app.post(self.endpoint, data=data)
        self.check_status_code(rv.status_code)
        msg = "login should have failed, invalid password"
        self.assertFalse(safe_json_loads(rv.data)["success"], msg=msg)


if __name__ == '__main__':
    unittest.main()
