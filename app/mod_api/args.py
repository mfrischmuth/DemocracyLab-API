from webargs import fields


class Args(object):
    
    
    """
    POST /api/issue
    
    Create a new issue
    
    post_issue = {
        'issue_name': <string>,                         // required
        'desc': <string>,                               // optional
        'values': [ <list of value names> ],            // required
        'objectives': [ <list of objective names> ],    // required
        'policies': [ <list of policy names> ]          // required
    } 
    """
   
    @staticmethod
    def parse_post_issue(args):
        errors = []
        data = {}
        if "issue_name" not in args:
            errors.append("Missing `issue_name` parameter")
        else:
            data["issue_name"] = args.get("issue_name")
        data["desc"] = args.get("desc", default="")
        for node_type in ["values", "objectives", "policies"]:
            # sometimes the nodes array will have key "<node type>[]"
            # with trailing [], and sometimes it does not have it
            # test both cases
            nodes = args.getlist(node_type)
            if not nodes:
                nodes = args.getlist(node_type + "[]")
            if len(nodes) <= 0: 
                errors.append("Missing `{0}` node list".format(node_type))
            data[node_type] = nodes
        return errors, data
    
    """
    GET /api/user
    GET /api/issue
    GET /api/value
    GET /api/objective/policy

    node in user, community, issue, value, objective, policy
    """
    get_node = {
        'id':fields.Str(required=True),
    }
    
    """
    GET /api/community/issue
    GET /api/issue/value
    GET /api/issue/objective
    GET /api/issue/policy
    """
    get_nodes = {
        'filter_id':fields.Str(required=True),
        'user_id':fields.Str(required=False)
    }
   
    """
    GET /api/community
    """
    get_community = {
        'id':fields.Str(required=False),
    }

    """
    POST /api/user
    """
    post_user = {
        'username':fields.Str(required=True),
        'password':fields.Str(required=True),
        'name':fields.Str(required=True),
        'city':fields.Str(required=True),
        'is_admin':fields.Boolean(required=False,default=False)
    }
    
    """
    POST /api/login
    """
    post_login = {
        'username':fields.Str(required=True),
        'password':fields.Str(required=True)
    }

    """
    POST /api/rank/<node>
    
    node in issue, value, objective, policy
    """
    post_rank = {
        'user_id':fields.Str(required=True),
        'node_id':fields.Str(required=True),
        'issue_id':fields.Str(required=False),
        'rank':fields.Int(required=True)
    }

    """
    POST /api/map/value/objective
    POST /api/map/objective/policy
    """
    post_map = {
        'user_id':fields.Str(required=True),
        'src_id':fields.Str(required=True),
        'dst_id':fields.Str(required=True),
        'strength':fields.Int(required=True)
    }
    
    """
    GET /api/summary/value?issue_id=<id>
    GET /api/summary/objective?issue_id=<id>
    GET /api/summary/policy?issue_id=<id>
    
    Get histogram data for how users ranked certain nodes
    """
    get_summary = {
        'issue_id':fields.Str(required=True)
    }

    """
    GET /api/sankey
    """
    get_sankey = {
        'issue_id':fields.Str(required=True)
    }
