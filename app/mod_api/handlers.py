from __future__ import absolute_import
import os

from flask import jsonify, session

from app import graph, CQLDIR
from app.mod_api.auth import Authenticate

from app.CorrXY import Corr


class Handler(object):
    """
    dlab-api endpoint handlers
    """

    @staticmethod
    def index():
        return jsonify(response="API Index")

    @staticmethod
    def post_login(args):
        print args
        success, error, is_admin = Authenticate.login(graph, session, args)
        return jsonify(success=success, error=error,is_admin=is_admin)

    @staticmethod
    def get_node(args, node_type):
        # use different handler if fetching a user
        if node_type == "User": return Handler._get_user(args)
       
        # lookup node and build json response
        node = graph.nodes.find(node_type, args["id"])
        if node:
            return jsonify(
                name=node.properties["name"],
                id=node.properties["node_id"]
            )
        return jsonify(error="No matching node: {0}".format(args["id"]))

    @staticmethod
    def _get_user(args):
        # lookup user node and build json response
        node = graph.nodes.find("User", args["id"])
        if node:
            return jsonify(
                id=node.properties["node_id"],
                name=node.properties["name"],
                city=node.properties["city"]
            )
        return jsonify(error="No matching user: {0}".format(args["id"]))

    @staticmethod
    def get_nodes(child_type, parent_type, args):
        kwargs = {}
        if parent_type:
            if "user_id" in args:
                kwargs = dict(
                    parent_label=parent_type,
                    parent_id=args["filter_id"],
                    user_id=args["user_id"]
                )
                data = graph.nodes.find_all_with_user_id(child_type, **kwargs)
            else:
                kwargs = dict(parent_label=parent_type, parent_id=args["filter_id"])
                data = graph.nodes.find_all(child_type, **kwargs)
        return jsonify(nodes=data)

    @staticmethod
    def post_rank(args, node_type):
        # apply ranking to node and return success status
        success, error = graph.user_rank(args, node_type)
        if success:
            return jsonify(success=success)
        return jsonify(success=success, error=error)

    @staticmethod
    def post_user(args):
        # create new user if it does not already exist
        user = args["username"]
        node, new_user = graph.create_user(args)
        if new_user:
            return jsonify(success=True, error="")
        else:
            error="User <{0}> already exists".format(user)
            return jsonify(success=False, error=error)
    
    @staticmethod
    def post_map(args, src_node, dst_node):
        success, error = graph.user_map(args, src_node, dst_node)
        return jsonify(success=success, error=error)

    @staticmethod
    def get_summary(args, node_type):
        success, response, invalid = graph.get_summary(args["issue_id"], node_type)
        if success:
            return jsonify(success=success, data=response, invalid=invalid)
        return jsonify(success=False, error=response)

    @staticmethod
    def post_issue(args):
        issue_id = graph.create_issue(args)
        return jsonify(success=True, issue_id=issue_id)

    @staticmethod
    def get_sentiment():
        filename = "value_objective_sentiment.cql"
        results = graph.execute_raw(os.path.join(CQLDIR, filename))
        for row in results:
            for i, pctdev in enumerate(row.pctdev):
                if pctdev > 0.2:
                    print(row.value, row.objective, i, row.stddev, pctdev)
        return jsonify({})

    @staticmethod
    def get_sankey(issue_id):
        valobj = os.path.join(CQLDIR, "sankey_value_objective.cql")
        objpol = os.path.join(CQLDIR, "sankey_objective_policy.cql")
        results_vo = graph.execute_raw(valobj, issue_id=issue_id)
        results_op = graph.execute_raw(objpol, issue_id=issue_id)
        
        nodes = []
        links = []
        node_lookup = {}
        
        for row in results_vo:
            if row.vid not in node_lookup:
                nodes.append(dict(name=row.vname))
                node_lookup[row.vid] = len(nodes) - 1
            if row.oid not in node_lookup:
                nodes.append(dict(name=row.oname))
                node_lookup[row.oid] = len(nodes) - 1
        for row in results_op:
            if row.pid not in node_lookup:
                nodes.append(dict(name=row.pname))
                node_lookup[row.pid] = len(nodes) - 1
        for row in results_vo:
            data = dict(
                source=node_lookup[row.vid],
                target=node_lookup[row.oid],
                value=Corr(row.vranks, row.oranks)
            )
            links.append(data)
        for row in results_op:
            corr = Corr(row.oranks, row.pranks)
            data = dict(
                source=node_lookup[row.oid], target=node_lookup[row.pid], value=corr
            )
            links.append(data)
        
        return jsonify(nodes=nodes, links=links)
