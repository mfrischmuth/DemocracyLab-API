from __future__ import absolute_import
import os
from os.path import basename, dirname

from flask import Blueprint, request, jsonify
from webargs.flaskparser import use_args

from app import graph
from app.mod_api.handlers import Handler
from app.mod_api.args import Args


"""
This file contains all of the routes our api can process. When a HTTP request
is made that mades one of our routes, that request will be passed to the
function registered to handle it. A HTTP response will be constructed and sent
back to the client.

The process for handling most requests is:

1. Parse parameters from request. For this we are using the webargs package.
It allows you to define the required and optional parameters in a dictionary
which is used to validate the request that all the required fields are present.

    + See `/app/mod_api/args.py`
    + Args definition is passed to function with `@use_args` decorator and
    then passed to handling function as an argument

2. Pass the request arguments to it's appropriate Handler. The Handler is
responsible for interacting with the graph to retrieve the requested data or
update the state of the system. All Handler methods will return a json response
object that is sent to the client.

    + See `/app/mod_api/handlers.py`
    + Most of the heavy lifting for the database is done using a graph
    convenience object. That provides wrappers for executing multi-stage
    queries in one call, as well as basic methods to fetch a single node
    or relationship. All direct database access should originate from that file.
    + See `/app/graph.py`

"""


mod_api = Blueprint('api', __name__, url_prefix='/api')


@mod_api.errorhandler(422)
def handle_bad_request(err):
    """
    default error handler when request arguments do not match required arguments
    as specified by use_args() input
    """
    data = getattr(err, 'data')
    message = data['exc'].messages if data else "invalid request"
    return jsonify({"error": message}), 422


@mod_api.route('')
def api_index():
    """
    api index
    """
    return Handler.index()


@mod_api.route('/user', methods=["POST"])
@use_args(Args.post_user)
def post_user(args):
    """
    create a new user
    """
    return Handler.post_user(args)


@mod_api.route('/login', methods=["POST"])
@use_args(Args.post_login)
def post_login(args):
    """
    authenticate user
    """
    return Handler.post_login(args)


@mod_api.route('/issue', methods=["POST"])
def post_issue():
    """
    create a new issue
    """
    errors, data = Args.parse_post_issue(request.form)
    if errors:
        return jsonify(success=False, errors=errors)
    return Handler.post_issue(data)


@mod_api.route('/user', methods=['GET'])
@mod_api.route('/issue', methods=['GET'])
@mod_api.route('/value', methods=['GET'])
@mod_api.route('/objective', methods=['GET'])
@mod_api.route('/policy', methods=['GET'])
@use_args(Args.get_node)
def get_node(args):
    """
    retrieve data about a node as specified by it's node_id
    """
    node = basename(request.path).capitalize()
    return Handler.get_node(args, node) 


@mod_api.route('/community', methods=['GET'])
@use_args(Args.get_community)
def get_community(args):
    """
    retrieve data about a node as specified by it's node_id
    """
    node = basename(request.path).capitalize()
    if "id" in args:
        return Handler.get_node(args, node) 
    else:
        return Handler.get_nodes(node, None, args) 


@mod_api.route('/community/issue', methods=['GET'])
@mod_api.route('/issue/value', methods=['GET'])
@mod_api.route('/issue/objective', methods=['GET'])
@mod_api.route('/issue/policy', methods=['GET'])
@use_args(Args.get_nodes)
def get_nodes(args):
    """
    retrieve all nodes of a given type
    """
    parent = basename(dirname(request.path)).capitalize()
    child = basename(request.path).capitalize()
    return Handler.get_nodes(child, parent, args) 


@mod_api.route('/rank/issue', methods=["POST"])
@mod_api.route('/rank/value', methods=["POST"])
@mod_api.route('/rank/objective', methods=["POST"])
@mod_api.route('/rank/policy', methods=["POST"])
@use_args(Args.post_rank)
def post_rank(args):
    """
    apply a ranking to a specific node as a user
    """
    node = os.path.basename(request.path).capitalize()
    return Handler.post_rank(args, node)


@mod_api.route('/map/value/objective', methods=["POST"])
@mod_api.route('/map/objective/policy', methods=["POST"])
@use_args(Args.post_map)
def post_map(args):
    """
    apply a mapping between nodes
    Value -> Objective || Objective -> Policy
    """
    src_node = os.path.basename(os.path.dirname(request.path)).capitalize()
    dst_node = os.path.basename(request.path).capitalize()
    return Handler.post_map(args, src_node, dst_node)


@mod_api.route('/summary/value', methods=['GET'])
@mod_api.route('/summary/objective', methods=['GET'])
@mod_api.route('/summary/policy', methods=['GET'])
@use_args(Args.get_summary)
def get_summary(args):
    """
    Generate summary for stacked bar chart visualization
    """
    node_type = basename(request.path).capitalize()
    return Handler.get_summary(args, node_type)


@mod_api.route('/sankey', methods=["GET"])
@use_args(Args.get_sankey)
def get_sankey(args):
    """
    Return data for sankey chart of correlation
    or ranking Value -> Objective and Objective -> Policy
    """
    return Handler.get_sankey(args["issue_id"])


"""
IN PROGRESS

Analyze sentiment of Value-Objective rankings by countig occurences
of the following ranking categories
"""
#@mod_api.route('/sentiment', methods=['GET'])
#def get_sentiment():
#    return Handler.get_sentiment(
