import hashlib
import six


class Authenticate(object):

    @staticmethod
    def login(graph, session, args):
        error = "invalid username-password combination"
        user = graph.nodes.find("User", args["username"])
        if not user:
            return False, error, False
        passhash = Authenticate.hashgen(args["username"], args["password"])
        if passhash != user.properties["passhash"]:
            return False, error, False
        return True, "", user["is_admin"]

    @staticmethod
    def hashgen(username, password):
        # sha256 can't take python 3.x strings as arguments
        if not isinstance(username, six.binary_type):
            username = username.encode('utf-8')
        if not isinstance(password, six.binary_type):
            password = password.encode('utf-8')

        salt = hashlib.sha256(username).hexdigest()
        if not isinstance(salt, six.binary_type):
            salt = salt.encode('utf-8')
        auth_hash = hashlib.sha256(salt + password).hexdigest()
        return auth_hash
