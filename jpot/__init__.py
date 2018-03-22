import json
import itertools
import types

try:
    import jsonpath_ng.ext
except:
    jsonpath_ng = None
try:
    import jsonpath.jsonpath
except:
    jsonpath = None
try:
    import objectpath
except:
    objectpath = None

def path_jsonpath_ng(data, expr):
    """Path expression engine using jsonpath_ng"""
    if jsonpath_ng is None: raise NotImplementedError("jsonpath_ng is not installed")
    return [item.value for item in jsonpath_ng.ext.parse(expr).find(data) or []]
path_jsonpath_ng.no_flatten = True

def path_jsonpath(data, expr):
    """Path expression engine using jsonpath"""
    if jsonpath is None: raise NotImplementedError("jsonpath is not installed")
    return jsonpath.jsonpath(data, expr, use_eval=False) or []
path_jsonpath.no_flatten = True

def path_objectpath(data, expr):
    """Path expression engine using objectpath"""
    if objectpath is None: raise NotImplementedError("objectpath is not installed")
    res = objectpath.Tree(data).execute(expr)
    if isinstance(res, (itertools.chain, types.GeneratorType)):
        res = list(res)
    else:
        res = [res]
    return res


class NoValue: pass

def first(values):
    if values:
        return values[0]
    else:
        return NoValue        
    
def transform(data, template, verbatim_str=False, path_engine=path_jsonpath_ng, debug=True):
    """Transforms data according to the template.

    verbatim_str
        if False, string values are interpreted as path
        expressions, if True they are copied verbatim to the output.
    path_engine
        path expression evaluation engine to use. Should be a function
        that takes arguments (data, expression) and returns list.
    """

    if debug:
        def path(data, expr):
            print("path(\n%s,\n%s)" % (json.dumps(data, indent=2), json.dumps(expr, indent=2)))
            res = path_engine(data, expr)
            print("=> %s" % json.dumps(res, indent=2))
            return res
    else:
        path = path_engine
    
    def transform(data, template):
        if isinstance(template, dict):
            if '$get' in template:
                result = first(path(data, template["$get"]))
                if '$transform' in template:
                    result = transform(result, template['$transform'])
                return result
            else:
                return {key: value
                        for key, value in
                        ((key, transform(data, value))
                         for key, value in template.items())
                        if value is not NoValue}
        elif isinstance(template, (list, tuple)):
            assert len(template) > 0, "List specification must include a JSONPath"
            if isinstance(template[0], list):
                return [transform(data, item) for item in template[0]]
            else:
                result = path(data, template[0])
                if len(template) < 2:
                    return result
                if not result:
                    return result
                if getattr(path_engine, 'no_flatten', False):
                    result = result[0]
                result = [value
                          for value
                          in (transform(item, template[1])
                              for item in result)
                          if value is not NoValue]
                return result
        elif isinstance(template, str) and not verbatim_str:
            if template.startswith(":"):
                return template[1:]
            else:
                return first(path(data, template))
        else:
            return template

    if debug:
        print("transform(\n%s,\n%s)" % (json.dumps(data, indent=2), json.dumps(template, indent=2)))

    res = transform(data, template)

    if debug:
        print("=> %s" % json.dumps(res, indent=2))
    
    return res

def _schema_is_array(schema):    
    for name in ("items", "additionalItems", "maxItems", "minItems", "uniqueItems", "contains"):
        if name in schema: return True
    return False

def _schema_transform(schema):
    if not isinstance(schema, dict):
        return schema
    schema = dict(schema)
    if 'items' in schema:
        if  isinstance(schema['items'], (list, tuple)):
            schema['items'] = [_schema_transform(item) for item in schema['items']]
        else:
            schema['items'] = _schema_transform(schema['items'])
    if 'additionalItems' in schema:
        schema['additionalItems'] = _schema_transform(schema['additionalItems'])
    if 'contains' in schema:
        schema['contains'] = _schema_transform(schema['contains'])
    if 'properties' in schema:
        schema['properties'] = {name: _schema_transform(value) for (name, value) in schema['properties'].items()}
    if 'patternProperties' in schema:
        schema['patternProperties'] = {name: _schema_transform(value) for (name, value) in schema['patternProperties'].items()}
    if 'additionalProperties' in schema:
        schema['additionalProperties'] = _schema_transform(schema['additionalProperties'])
    if 'dependencies' in schema:
        def transform_dependency(dep):
            if isinstance(dep, (list, tuple)):
                return dep
            else:
                return _schema_transform(dep)
        schema['dependencies'] = {name: transform_dependency(value) for (name, value) in schema['dependencies'].items()}
    if 'if' in schema:
        del schema['if']
        if 'anyOf' not in schema:
            schema['anyOf'] = []
        if 'then' in schema:
            schema['anyOf'] = schema['anyOf'] + [schema.pop('then')]
        if 'else' in schema:
            schema['anyOf'] = schema['anyOf'] + [schema.pop('else')]

    if 'allOf' in schema:
        schema['allOf'] = _schema_transform(schema['allOf'])
    if 'anyOf' in schema:
        schema['anyOf'] = _schema_transform(schema['anyOf'])
    if 'oneOf' in schema:
        schema['oneOf'] = _schema_transform(schema['oneOf'])

    if _schema_is_array(schema):
        return {"anyOf": [
            {"items": [{"$ref": "#/definitions/jsonpath"}]},
            {"items": [{"$ref": "#/definitions/jsonpath"}, schema]},
            schema]}
    else:
        return {"anyOf": [{"$ref": "#/definitions/jsonpath"}, schema]}
        
def schema_transform(schema):
    schema = dict(schema)
    definitions = schema.pop('definitions', {})
    schema = _schema_transform(schema)
    definitions = {name:_schema_transform(value)
                   for name, value in definitions.items()}
    definitions['jsonpath'] = {'type': 'object',
                               'title': 'Source data',
                               'properties': {
                                   '$get': {
                                       'type': 'string',
                                       'title': 'JSON-path'
                                   },
                                   '$transform': {
                                       'type': 'object',
                                       'title': 'Optional tranform to apply to matched values'
                                   }
                               }
    }
    schema['definitions'] = definitions
    return schema
