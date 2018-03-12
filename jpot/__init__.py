import jsonpath

class NoValue: pass

def first(values):
    if values:
        return values[0]
    else:
        return NoValue        
    
def transform(data, template):
    if isinstance(template, dict):
        return {key: value
                for key, value in
                ((key, transform(data, value))
                 for key, value in template.items())
                if value is not NoValue}
    elif isinstance(template, (list, tuple)):
        assert len(template) > 0, "List specification must include a JSONPath"
        result = jsonpath.jsonpath(data, template[0], use_eval=False) or []
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
    elif isinstance(template, str):
        return first(jsonpath.jsonpath(data, template, use_eval=False))
    else:
        assert False, "Unknown data type for template: %s" % (type(template),)
