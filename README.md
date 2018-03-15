# python-jsonpath-object-transform

Python implementation of https://github.com/dvdln/jsonpath-object-transform supporting the same language and API
for transforming JSON documents using JSONPath.

    >>> from jpot import *
    >>> transform({"some":{"crazy":[{"foo": 1}, {"foo": 2}]}}, {"x":['$..crazy', {"a":'$.foo'}]})["x"]
    [{'a': 1}, {'a': 2}]

# Extensions over the javascript version

## Verbatim lists

A list wrapped inside another list [[]] produces a list as output,
whose elements are the result of applying the elements of the list in
the template to the data each at a time.

    >>> from jpot import *
    >>> transform({"foo": 47, "bar": 11}, {"my_synthesized": [["$.foo", "$.bar", {"gazonk": "$.foo"}]]})
    {"my_synthesized": [47, 11, {"gazonk": 11}]}

## Verbatim strings

    >>> transform(something, {"foo": ":Some text"})
    "Some text"

## Other verbatim values

    >>> transform(something, {"foo": 47})
    47
    >>> transform(something, {"foo": true})
    true
    