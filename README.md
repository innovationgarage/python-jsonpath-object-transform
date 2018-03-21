# python-jsonpath-object-transform

Python implementation of https://github.com/dvdln/jsonpath-object-transform supporting the same language and API
for transforming JSON documents using JSONPath.

    >>> from jpot import *
    >>> transform({"some":{"crazy":[{"foo": 1}, {"foo": 2}]}}, {"x":['$..crazy', {"a":'$.foo'}]})["x"]
    [{'a': 1}, {'a': 2}]

# Extensions over the javascript version

## Multiple path expression engines

Support for path expressions using any of

  * http://objectpath.org
  * https://github.com/h2non/jsonpath-ng
  * https://pypi.python.org/pypi/jsonpath

## Chained transforms

Transforms for values returned by path expressions

    >>> transform({"fie": {"gazonk": 47, "nana": 4}}, {"bar": {"$get": "$.fie", "$transform": {"blupp": "$.nana"}}})
    {'bar': {'blupp': 4}}

## Verbatim lists

A list wrapped inside another list [[]] produces a list as output,
whose elements are the result of applying the elements of the list in
the template to the data each at a time.

    >>> from jpot import *
    >>> transform({"foo": 47, "bar": 11}, {"my_synthesized": [["$.foo", "$.bar", {"gazonk": "$.foo"}]]})
    {"my_synthesized": [47, 11, {"gazonk": 11}]}

## Verbatim strings

    >>> transform({"fie": 1}, {"foo": "Some text", "bar": {"$get": "$.fie"}}, verbatim_str=True)
    {"foo": "Some text", "bar": 1}

## Other verbatim values

    >>> transform(something, {"foo": 47})
    47
    >>> transform(something, {"foo": true})
    true
    