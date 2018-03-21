from jsonpath_ng.ext import parse

class NoValue: pass

def first(values):
    if values:
        return values[0]
    else:
        return NoValue        
    
def transform(data, template, verbatim_str=False):
    if isinstance(template, dict):
        if '$get' in template:
            result = first(parse(template["$get"]).find(data)).value
            if '$transform' in template:
                result = transform(result, template['transform'])
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
            result = [item.value for item in parse(template[0]).find(data)] or []
            if len(template) < 2:
                return result
            if not result:
                return result
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
            return first(parse(template).find(data)).value
    else:
        return template


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
