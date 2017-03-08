import six
import json


def safe_json_loads(data):
    """
    Provides py2/py3 compatible way of retrieving data from a json string
    """
    if isinstance(data, six.string_types):
        return json.loads(data)
    else:
        return json.loads(data.decode('utf-8'))
