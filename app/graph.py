from __future__ import absolute_import
from py2neo import Graph as NeoGraph, Node, Relationship

from app.mod_api.auth import Authenticate
import uuid


class Nodes(object):
    def __init__(self, graph):
        self.graph = graph

    def find(self, label, node_id):
        return self.graph.find_one(label, "node_id", node_id)

    def find_all(self, label, **kwargs):
        """
        Find all nodes in graph of a given `label` type

        If `parent_label` and `parent_id` keyword params are present then only
        return nodes of type `label` that are children of the parent node,
        otherwise return all nodes of type `label`
        """
        parent = None
        if "parent_label" in kwargs and "parent_id" in kwargs:
            parent = self.find(kwargs["parent_label"], kwargs["parent_id"])
            # TODO: Unfound parent should give none/error
            # When all node types have been implemented, change to that behavior

        if parent:
            cypher = "MATCH (p:`{}` {{node_id: {{p_id}}}})-->(n:`{}`) RETURN n"
            cypher = cypher.format(kwargs['parent_label'], label)
            return [r.n.properties for r in self.graph.cypher.stream(
                cypher, p_id=kwargs['parent_id'])]
            # for link in parent.match_outgoing():
            #     if label in link.end_node.labels:
            #         nodes.append(link.end_node.properties)
            # return nodes
        else:
            return [node.properties for node in self.graph.find(label)]
            # nodes = [node.properties for node in self.graph.find(label)]
            # return nodes

    def find_all_with_user_id(self, label, user_id, **kwargs):
        """
        Similar to find_all, but filter with a specific user_id
        """
        query = """MATCH (p:`%s` {node_id: {p_id}})-->(n:`%s`),
                   (n)<-[r]-(u:User {node_id: {u_id}})
                   RETURN r.rank as rank, n.node_id as node_id"""
        query = query % (kwargs['parent_label'], label)
        return [{'rank': m.rank, 'node_id': m.node_id} for m in
                self.graph.cypher.stream(
                    query, p_id=kwargs['parent_id'], u_id=user_id)]
        # user = self.find("User", user_id)
        # if not user:
        #     return []
        # parent = self.find(kwargs["parent_label"], kwargs["parent_id"])
        # data = []
        # for link in parent.match():
        #     link_user = self.graph.match_one(
        #         start_node=user, end_node=link.end_node)
        #     if link_user and label in link_user.end_node.labels:
        #         data.append(dict(
        #             rank=link_user.properties["rank"],
        #             node_id=link_user.end_node.properties["node_id"]
        #         ))
        # return data

    def create(self, node_type, properties):
        node = Node(node_type, **properties)
        self.graph.create(node)
        return node, True

    def delete(self, node_type, node_id):
        node = self.find(node_type, node_id)
        if node:
            self.graph.delete(node)
            return True
        return False


class Links(object):
    def __init__(self, graph):
        self.graph = graph

    def find(self, start_node, end_node, rel_type):

        return self.graph.match_one(
            start_node=start_node, end_node=end_node, rel_type=rel_type)

    def create(self, src, dst, link_type, properties):
        link = self.find(src, dst, link_type)
        if not link:
            link = Relationship(src, link_type, dst, **properties)
            self.graph.create(link)
        return link

    def delete(self, start, end, link_type):
        if start and end:
            link = self.find(start, end, link_type)
            if link:
                self.graph.delete(link)
                return True
        return False


class Graph(object):

    def __init__(self, neo4j_uri):
        self.graph = NeoGraph(neo4j_uri)
        self.nodes = Nodes(self.graph)
        self.links = Links(self.graph)

    def execute_raw(self, cqlfile, **kwargs):
        with open(cqlfile, 'r') as query:
            return self.graph.cypher.execute(query.read(), parameters=kwargs)

    def create_user(self, args):
        node = self.nodes.find("User", args["username"])
        if "is_admin" not in args:
            args["is_admin"] = False
        if not node:
            passhash = Authenticate.hashgen(args["username"], args["password"])
            properties = {
                'node_id': args["username"],
                'name': args["name"],
                'city': args["city"],
                'passhash': passhash,
                'is_admin': args["is_admin"]
            }
            return self.graph.create(Node("User", **properties))[0], True
        return node, False

    def create_issue_nodes(
            self, parent, names, node_type, link_type="HAS", link_prop=None):
        # support function for create_issue
        # create nodes of 1 type (value/objective/policy) and link those
        # to the sourceNode, with specified linkType and properties
        if link_prop is None:
            link_prop = {}
        nodes = []
        for name in names:
            properties = {'node_id': str(uuid.uuid4()), 'name': name}
            node = Node(node_type, **properties)
            self.graph.create(
                node, Relationship(parent, link_type, node, **link_prop))
            nodes.append(node)
        return nodes

    def create_issue(self, args):
        # create a new issue Node
        # assign a random node_id using python uuid module
        # below try uuid4, uuid1 works as well
        issue_properties = dict(
                node_id=str(uuid.uuid4()),
                name=args["issue_name"],
                desc=args["desc"]
            )
        issue_node = Node("Issue", **issue_properties)
        self.graph.create(issue_node)
 
        # create new nodes and links for values/objectives/policies
        # associated with the new issue
        self.create_issue_nodes(issue_node, args["values"], "Value")
        self.create_issue_nodes(issue_node, args["objectives"], "Objective")
        self.create_issue_nodes(issue_node, args["policies"], "Policy")
        return issue_properties["node_id"]

    def user_rank(self, args, node_type):
        # success = False
        # errors = []

        user = self.nodes.find("User", args["user_id"])
        if not user:
            return False, "invalid user_id"

        node = self.nodes.find(node_type, args["node_id"])
        if not node:
            return False, "invalid node_id"

        link, = self.graph.create_unique(Relationship(user, "RANKS", node))
        link["rank"] = args["rank"]
        link.push()
        return True, ""

    def user_map(self, args, src_node, dst_node):
        # TODO refactor this into smaller units

        # success = False
        errors = []

        # retrieve nodes and existing links
        user = self.nodes.find("User", args["user_id"])
        if not user:
            errors.append("invalid user_id")
        src = self.nodes.find(src_node, args["src_id"])
        if not src:
            errors.append("invalid src_id")
        dst = self.nodes.find(dst_node, args["dst_id"])
        if not dst:
            errors.append("invalid dst_id")
        src_link = self.links.find(user, src, "RANKS")
        if not src_link:
            errors.append("user has not ranked src_node")
        dst_link = self.links.find(user, dst, "RANKS")
        if not dst_link:
            errors.append("user has not ranked dst_node")
        if errors:
            return False, ", ".join(errors)

        # fetch map node or create if it doesn't exist
        map_id = "{0}-{1}".format(args["src_id"], args["dst_id"])
        map_node = self.graph.merge_one("Map", 'node_id', map_id)
        self.graph.create_unique(
            (src, "MAPS", map_node), (map_node, "MAPS", dst))

        new_props = {
            "strength": args["strength"],
            "src_rank": src_link["rank"],
            "dst_rank": dst_link["rank"]
        }
        # Create (or return existing) user-map link, then update properties
        user_map_link, = self.graph.create_unique(
            Relationship(user, "MAPS", map_node))
        user_map_link.properties.update(new_props)
        self.graph.push()
        return True, ""

    def get_summary(self, issue_id, node_type):
        issue = self.nodes.find("Issue", issue_id)
        if not issue:
            return False, "issue <{0}> does not exist".format(issue_id), []
        query = """
            MATCH (v:`{0}`)<-[:HAS]-(i:Issue)
            WHERE i.node_id = {{issue_id}}
            WITH v, [-2, -1, 0, 1, 2] as coll UNWIND coll AS rank
            OPTIONAL MATCH (u:User)-[r:RANKS]->(v)
            WHERE r.rank = rank
            WITH
                v.node_id AS node_id,
                v.name AS name,
                rank,
                count(u) AS count
            ORDER BY
                node_id, rank
            RETURN node_id, name, collect(count) as data
        """.format(node_type)
        nodes = {row.node_id: {'name': row.name, 'data': row.data}
                 for row in self.graph.cypher.stream(query, issue_id=issue_id)}
        invalid_query = """
        MATCH (:User)-[r:RANKS]-(:`{0}`)<-[:HAS]-(i:Issue)
        WHERE i.node_id = {{issue_id}}
        AND (r.rank < -2 OR r.rank > 2)
        RETURN r.rank as rank
        """.format(node_type)
        invalid = [row.rank for row in
                   self.graph.cypher.stream(invalid_query, issue_id=issue_id)]
        return True, nodes, invalid
