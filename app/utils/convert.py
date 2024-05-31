


from enum import Enum


def object_to_dict(obj):
    if isinstance(obj, Enum):
            return obj.name
    elif isinstance(obj, (int, float, bool, str)):
        return obj
    elif isinstance(obj, dict):
        return {k: object_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, object):
        if hasattr(obj, '__dict__'):
            return {k: object_to_dict(v) for k, v in vars(obj).items()}
        else:
            return obj
    else:
        return obj