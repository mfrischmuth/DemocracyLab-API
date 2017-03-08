from __future__ import print_function
import sys
from os.path import dirname, abspath
import unittest

# add parent directory to path to allow importing app
root = dirname(dirname(dirname(abspath(__file__))))
sys.path.append(root)


from app import app, graph


class CypherRawTest(unittest.TestCase):
           
    def test_basic(self):
        cypher = graph.graph.cypher
        query = """
            MATCH (u:User)-[r:RANKS]-(v:Value)
            RETURN
                r.rank AS rank,
                v.node_id AS node_id,
                count(u.node_id) AS count;
        """
        results = cypher.execute(query)
        # for row in results:
        #     print(row.rank, row.node_id, row.count)


if __name__ == '__main__':
    unittest.main()
