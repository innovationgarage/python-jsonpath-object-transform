from jsonpath_ng.ext import parse

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
    elif isinstance(template, str):
        return first(parse(template).find(data)).value
    else:
        assert False, "Unknown data type for template: %s" % (type(template),)
