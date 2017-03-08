import sys
from os.path import basename, dirname, abspath
import json
import unittest
import uuid

import py2neo

# add parent directory to path to allow importing app
root = dirname(abspath(__file__))
sys.path.append(root)

from app import app, graph

PASSWORD = "password"

class Handler(object):

    def __init__(self):
        self.nodes = []
        self.links = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_link(self, link):
        self.links.append(link)

    def clean_up(self):
        graph.graph.delete(*self.links)
        graph.graph.delete(*self.nodes)


class Node(object):
    
    def __init__(self, handler, node_type):
        self.node_type = node_type
        self.node_id = str(uuid.uuid4())
        self.name = "{0}-{1}".format(self.node_type, self.node_id)
        properties = dict(node_id=self.node_id, name=self.name) 
        self.node, self.success = graph.nodes.create(self.node_type, properties)
        if self.success: handler.add_node(self.node)


class User(object):

    def __init__(self, handler):
        self.node_type = "User"
        self.node_id = str(uuid.uuid4())
        self.name = "{0}-{1}".format("User", self.node_id)
        self.data = dict(
            username=self.node_id,
            password=PASSWORD,
            name="TestUser",
            city="Portland"
        )
        self.node, self.success = graph.create_user(self.data)
        if self.success: handler.add_node(self.node)


class Link(object):

    def __init__(self, handler, src, dst, rel_type):
        self.src = src
        self.dst = dst
        self.link = graph.links.create(src, dst, rel_type, {})
        handler.add_link(self.link)


class Rank(Link):

    def __init__(self, handler, src, dst, rank):
        self.src = src
        self.dst = dst
        self.link = graph.links.create(src, dst, "RANKS", dict(rank=rank))
        handler.add_link(self.link)
