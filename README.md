# python-jsonpath-object-transform

Python implementation of https://github.com/dvdln/jsonpath-object-transform supporting the same language and API
for transforming JSON documents using JSONPath.

    >>> from jpot import *
    >>> transform({"some":{"crazy":[{"foo": 1}, {"foo": 2}]}}, {"x":['$..crazy', {"a":'$.foo'}]})["x"]
    >>> [{'a': 1}, {'a': 2}]
