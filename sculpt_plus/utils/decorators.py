from functools import wraps


def singleton(orig_cls):
    orig_new = orig_cls.__new__
    instance = None

    @classmethod
    def get_instance(cls):
        nonlocal instance
        return instance
    
    @classmethod
    def clear_instance(cls):
        nonlocal instance
        if instance is not None:
            del instance
            instance = None

    @classmethod
    def set_instance(cls, data):
        nonlocal instance
        instance = data

    @wraps(orig_cls.__new__)
    def __new__(cls, *args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = orig_new(cls, *args, **kwargs)
        return instance
    orig_cls.__new__ = __new__
    orig_cls.get_instance = get_instance
    orig_cls.set_instance = set_instance
    return orig_cls
